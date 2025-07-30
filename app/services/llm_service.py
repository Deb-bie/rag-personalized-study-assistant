from typing import Dict, Any, List, Optional
# from openai import OpenAI # type: ignore
from ollama import AsyncClient # type: ignore
from app.core.config import settings
from app.core.exceptions import StudyAssistantException


class LLMService:
    def __init__(self):
        self.client = AsyncClient(host='http://localhost:11434')
        self.model = "mistral"
    
    async def generate_chat_response(
        self,
        query: str,
        context: str = "",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        try:
            messages = []
            
            # System prompt
            system_prompt = """
            
                You are a helpful study assistant. You help students learn by answering questions based on their study materials. 
                
                When provided with context from documents, use that information to give accurate and helpful answers. 
                If the context doesn't contain relevant information, say so clearly.
                Always be encouraging and supportive in your responses.
            """
            
            if context:
                system_prompt += f"\n\nContext from study materials:\n{context}"

            prompt = f"{system_prompt}\n\nUser: {query}"

            response = await self.client.chat(model=self.model, messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ])
            
            return response['message']['content'].strip()

            
            # messages.append({"role": "system", "content": system_prompt})
            
            # # Add conversation history
            # if conversation_history:
            #     messages.extend(conversation_history)
            
            # # Add current query
            # messages.append({"role": "user", "content": query})
            
            # response = await self.client.chat.completions.create(
            #     model=self.model,
            #     messages=messages,
            #     max_tokens=1000,
            #     temperature=0.7
            # )
            
            # return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise StudyAssistantException(f"Error generating LLM response: {str(e)}")
    
    async def generate_summary(self, text: str) -> str:
        try:

            prompt = f"Summarize the following text concisely:\n\n{text}"

            response = await self.client.chat(
                model=self.model, 
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful summarizer."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
            ])

            return response['message']['content'].strip()


            # response = await self.client.chat.copletions.create(
            #     model=self.model,
            #     messages=[
            #         {"role": "system", "content": "Summarize the following text concisely, focusing on key concepts and main points."},
            #         {"role": "user", "content": text}
            #     ],
            #     max_tokens=300,
            #     temperature=0.3
            # )
            
            # return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise StudyAssistantException(f"Error generating summary: {str(e)}")
    
    async def generate_quiz_questions(
        self,
        content: str,
        num_questions: int = 5
    ) -> List[Dict[str, Any]]:
        try:
            prompt = f"""Based on the following content, generate {num_questions} multiple-choice questions with 4 options each. 
            Format as JSON with this structure:
            {{
                "questions": [
                    {{
                        "question": "Question text",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": 0,
                        "explanation": "Why this is correct"
                    }}
                ]
            }}
            
            Content: {content}"""

            response = await self.client.chat(
                model=self.model, 
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a quiz generator. Generate educational multiple-choice questions."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )

            import json
            result = json.loads(response['message']['content'].strip())
            return result.get("questions", [])
            
            # response = await self.client.chat.completions.create(
            #     model=self.model,
            #     messages=[
            #         {"role": "system", "content": "You are a quiz generator. Generate educational multiple-choice questions."},
            #         {"role": "user", "content": prompt}
            #     ],
            #     max_tokens=1500,
            #     temperature=0.5
            # )
            
            # import json
            # result = json.loads(response.choices[0].message.content.strip())
            # return result.get("questions", [])
            
        except Exception as e:
            raise StudyAssistantException(f"Error generating quiz questions: {str(e)}")