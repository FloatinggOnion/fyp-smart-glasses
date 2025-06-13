"use node"
import { v } from "convex/values";
import  { action } from "./_generated/server";
import { GoogleGenAI} from "@google/genai";

export const geminiReply = action({
    args: {
        prompt: v.string(),
    },
    handler: async (ctx, args) => {
        const key = process.env.GEMINI_API!;
        if (!key) {
            console.error("🛑 Missing GEMINI_AP");
            throw new Error("Server is misconfigured");
          }
      
        const ai = new GoogleGenAI({ apiKey: key });
      
  
        try{
            const response = await ai.models.generateContent({
                model: "gemini-2.0-flash-001",
                contents: args.prompt,
              });
              console.log(response.text);

              return response.text;
        }
        catch(error){
            console.error("Error generating response:", error);
            throw new Error("Failed to generate response");
        }

    }
        

})