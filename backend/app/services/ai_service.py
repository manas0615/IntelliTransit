"""
IntelliTransit AI Assistant Service.
Integrates Google Gemini 2.5 Flash with 6 authoritative tools and graceful rule-based fallback.
"""
import re
import json
import logging
import requests
from typing import Any, Dict, List, Optional
from backend.app.config import Config
from backend.app.services.ai_tools import AIToolExecutor, GEMINI_TOOLS_DECLARATION

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are IntelliTransit AI, an intelligent multimodal journey assistant for Pune, India.
You assist commuters with planning transit trips using PMPML Buses, Pune Metro, and Taxis.
You have access to 6 specialized tools to plan journeys, fetch tickets, view passes, and inspect user history.
Always use tools whenever the user asks for trip planning or account data.
Provide clear, helpful, and concise transit summaries including modes, travel time, and estimated fares.
Locations must be within the Pune metropolitan area.
"""


class AIService:
    """Orchestrates conversations with Gemini 2.5 Flash and tool executions."""

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id
        self.executor = AIToolExecutor(user_id=user_id)
        self.api_key = Config.GEMINI_API_KEY

    def chat(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Process a user prompt.
        If Gemini API key is available, queries Gemini with function calling.
        Otherwise falls back to built-in local intent engine using the exact same backend tools.
        """
        if self.api_key and len(self.api_key) > 5:
            try:
                res = self._chat_with_gemini(message, history or [])
                res["mode"] = "GEMINI"
                res["model"] = "Gemini 2.5 Flash"
                return res
            except Exception as e:
                logger.warning("Gemini API call failed (%s), falling back to local intent parser.", e)
                res = self._chat_fallback(message)
                res["mode"] = "DEMO_FALLBACK"
                res["model"] = "Local Demo AI Fallback"
                return res
        else:
            res = self._chat_fallback(message)
            res["mode"] = "DEMO_FALLBACK"
            res["model"] = "Local Demo AI Fallback"
            return res

    def _chat_with_gemini(self, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Call Gemini REST endpoint with tools."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        
        # Build contents array from history and message
        contents = []
        for turn in history[-6:]:  # last 6 turns context
            role = "user" if turn.get("role") == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": turn.get("content", "")}]
            })
        contents.append({
            "role": "user",
            "parts": [{"text": message}]
        })

        # Format function declarations for Gemini
        tools_payload = [{
            "function_declarations": [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"]
                }
                for t in GEMINI_TOOLS_DECLARATION
            ]
        }]

        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": contents,
            "tools": tools_payload,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024
            }
        }

        resp = requests.post(url, json=payload, timeout=12)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")

        res_json = resp.json()
        candidates = res_json.get("candidates", [])
        if not candidates:
            return {"reply": "I'm sorry, I could not generate a response at this moment.", "tools_called": []}

        first_cand = candidates[0]
        content_parts = first_cand.get("content", {}).get("parts", [])

        # Check for function calls
        tool_results = []
        final_text = ""

        for part in content_parts:
            if "text" in part:
                final_text += part["text"] + "\n"
            elif "functionCall" in part:
                func_call = part["functionCall"]
                fn_name = func_call.get("name")
                fn_args = func_call.get("args", {})
                
                tool_output = self.executor.execute_tool(fn_name, fn_args)
                tool_results.append({
                    "tool": fn_name,
                    "arguments": fn_args,
                    "output": tool_output
                })

        # If function was called, we can summarize tool output or return directly
        if tool_results and not final_text.strip():
            # Build natural summary from tool output
            t0 = tool_results[0]
            final_text = self._summarize_tool_output(t0["tool"], t0["output"])

        return {
            "reply": final_text.strip(),
            "tools_called": tool_results
        }

    def _chat_fallback(self, message: str) -> Dict[str, Any]:
        """
        Rule-based intent classifier executing the exact same 6 tools when offline/without key.
        """
        msg_lower = message.lower().strip()
        tool_results = []
        reply = ""

        # Intent 1: Active Tickets
        if any(w in msg_lower for w in ["my ticket", "active ticket", "show ticket", "my tickets"]):
            out = self.executor.execute_tool("get_active_tickets", {})
            tool_results.append({"tool": "get_active_tickets", "output": out})
            tickets = out.get("active_tickets", [])
            if tickets:
                reply = f"You have {len(tickets)} active transit ticket(s):\n"
                for t in tickets[:3]:
                    reply += f"• {t.get('origin')} → {t.get('destination')} (Fare: ₹{t.get('fare')})\n"
            else:
                reply = "You currently have no active tickets. Plan a journey to book one!"

        # Intent 2: Active Passes
        elif any(w in msg_lower for w in ["my pass", "active pass", "show pass", "my passes"]):
            out = self.executor.execute_tool("get_active_passes", {})
            tool_results.append({"tool": "get_active_passes", "output": out})
            passes = out.get("active_passes", [])
            if passes:
                reply = f"You have {len(passes)} active transit pass(es):\n"
                for p in passes[:3]:
                    reply += f"• {p.get('pass_type')} Pass (Token: {p.get('pass_token')})\n"
            else:
                reply = "You currently have no active transit passes. You can purchase a Daily, Weekly, or Monthly pass in the Passes section."

        # Intent 3: Journey History
        elif any(w in msg_lower for w in ["history", "past trips", "previous journeys", "my journeys", "recent journeys"]):
            out = self.executor.execute_tool("get_journey_history", {"limit": 5})
            tool_results.append({"tool": "get_journey_history", "output": out})
            history = out.get("history", [])
            if history:
                reply = f"Here are your last {len(history)} searched journeys:\n"
                for h in history:
                    reply += f"• {h.get('origin_name')} → {h.get('destination_name')}\n"
            else:
                reply = "No previous journey searches found in your history."

        # Intent 4: User Preferences
        elif any(w in msg_lower for w in ["preference", "my preferences", "settings", "travel preferences"]):
            out = self.executor.execute_tool("get_user_preferences", {})
            tool_results.append({"tool": "get_user_preferences", "output": out})
            pref = out.get("preferences", {})
            if pref and isinstance(pref, dict):
                reply = f"Your current routing preferences:\n• Priority Profile: {pref.get('routing_preference', 'BALANCED')}\n• Max Walking: {pref.get('max_walking_distance_meters', 1000)}m"
            else:
                reply = "No custom preferences configured yet. Using default BALANCED routing profile."

        # Intent 5: Journey Details (Inspect specific or latest journey)
        elif any(w in msg_lower for w in ["about this journey", "journey detail", "details of journey", "tell me about this journey"]):
            uuid_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', msg_lower)
            j_id = uuid_match.group(0) if uuid_match else None
            if not j_id:
                # Retrieve latest journey from user history
                hist = self.executor.execute_tool("get_journey_history", {"limit": 1})
                if hist.get("history") and len(hist["history"]) > 0:
                    j_id = hist["history"][0].get("journey_id")

            if j_id:
                out = self.executor.execute_tool("get_journey_details", {"journey_id": j_id})
                tool_results.append({"tool": "get_journey_details", "output": out})
                j = out.get("journey", {})
                legs = out.get("legs", [])
                modes_str = " → ".join(l.get("mode", "") for l in legs) if legs else "MULTIMODAL"
                reply = (
                    f"Trip Details for {j.get('origin_name')} → {j.get('destination_name')}:\n"
                    f"• Modes: {modes_str}\n"
                    f"• Duration: {j.get('total_duration_min', 0)} mins\n"
                    f"• Estimated Fare: ₹{float(j.get('estimated_fare') or 0):.2f}\n"
                    f"• Segments / Legs: {len(legs)}"
                )
            else:
                reply = "No previous journey found in your history to inspect. Plan a route first!"

        # Intent 6: Journey Planning (e.g. "from Swargate to Pune Station", "how to reach Hinjawadi from Kothrud", "travel from Kothrud to Pune Station")
        elif ("from " in msg_lower and " to " in msg_lower) or any(w in msg_lower for w in ["reach", "go to", "route", "plan", "travel"]):
            origin, dest = self._extract_origin_dest(message)
            if origin and dest:
                # Detect preference profile
                pref = "BALANCED"
                if "fast" in msg_lower: pref = "FASTEST"
                elif "cheap" in msg_lower: pref = "CHEAPEST"
                elif "transfer" in msg_lower: pref = "MIN_TRANSFERS"
                elif "walk" in msg_lower: pref = "LEAST_WALKING"

                out = self.executor.execute_tool("plan_journey", {
                    "origin_name": origin,
                    "destination_name": dest,
                    "preference_profile": pref
                })
                tool_results.append({"tool": "plan_journey", "arguments": {"origin_name": origin, "destination_name": dest, "preference_profile": pref}, "output": out})
                reply = self._summarize_tool_output("plan_journey", out)
            else:
                reply = "I'd be happy to plan your trip! Please provide origin and destination (e.g. 'Plan journey from Swargate to Pune Station')."

        # General Help / Greeting
        else:
            reply = (
                "Hello! I am your IntelliTransit AI Companion (Demo AI Mode). I can assist you with:\n"
                "• 🗺️ Planning routes across PMPML Bus, Pune Metro, and Taxis (e.g., 'How do I travel from Kothrud to Pune Station?')\n"
                "• 🎫 Viewing active tickets ('Show my active tickets')\n"
                "• 💳 Checking transit passes ('Show my passes')\n"
                "• 📜 Viewing recent journeys ('Tell me about my recent journeys')\n"
                "• ⚙️ Checking travel preferences ('What are my travel preferences?')\n"
                "How may I assist your travel today?"
            )

        return {
            "reply": reply,
            "tools_called": tool_results
        }

    def _extract_origin_dest(self, text: str) -> tuple[Optional[str], Optional[str]]:
        """Extract origin and destination from natural language sentences."""
        # Pattern 1: from <origin> to <dest>
        m1 = re.search(r'from\s+([A-Za-z0-9\s]+?)\s+to\s+([A-Za-z0-9\s\?]+)', text, re.IGNORECASE)
        if m1:
            return m1.group(1).strip(), m1.group(2).replace("?", "").strip()

        # Pattern 2: how to reach <dest> from <origin>
        m2 = re.search(r'reach\s+([A-Za-z0-9\s]+?)\s+from\s+([A-Za-z0-9\s\?]+)', text, re.IGNORECASE)
        if m2:
            return m2.group(2).replace("?", "").strip(), m2.group(1).strip()

        # Pattern 3: go to <dest> from <origin>
        m3 = re.search(r'go\s+to\s+([A-Za-z0-9\s]+?)\s+from\s+([A-Za-z0-9\s\?]+)', text, re.IGNORECASE)
        if m3:
            return m3.group(2).replace("?", "").strip(), m3.group(1).strip()

        return None, None

    def _summarize_tool_output(self, tool_name: str, output: Dict[str, Any]) -> str:
        """Create human-readable message from tool execution result."""
        if "error" in output:
            return f"⚠️ {output['error']}"

        if tool_name == "plan_journey":
            itineraries = output.get("itineraries", [])
            if not itineraries:
                return "No transit routes found between these locations."
            best = itineraries[0]
            legs = best.get("legs", [])
            modes = " → ".join(l.get("mode") for l in legs)
            return (
                f"✅ Optimal Route: {output.get('origin', {}).get('name')} to {output.get('destination', {}).get('name')}\n"
                f"• Modes: {modes}\n"
                f"• Total Duration: {best.get('total_duration_minutes', 0)} mins\n"
                f"• Total Fare: ₹{best.get('total_fare', 0.0):.2f}\n"
                f"• Carbon Footprint: {best.get('carbon_footprint_kg', 0.0)} kg CO₂\n"
                f"• Recommendation: {best.get('explanation', 'Optimal balanced itinerary.')}"
            )

        return json.dumps(output)
