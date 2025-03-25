import openai

def simple_request(request):
    print("Received a request at /chat endpoint AHHHHHHHHHHHHHHHHHHHHHHHHHH")
    data = request.get_json(force=True)
    user_message = data.get("message")  # Get user message

    if not data or not user_message:
        return {"reply": "I didn't understand that."}

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # GPT-4 if available
            messages=[{"role": "system", "content": "You are a helpful AI assistant."},
                      {"role": "user", "content": user_message}]
        )
        ai_reply = response["choices"][0]["message"]["content"]
        print(ai_reply)
        return {"reply": ai_reply}  # Send AI reply back to frontend
    except Exception as e:
        print(f"Chat error: {e}")
        return {"reply": "Error connecting to AI."}