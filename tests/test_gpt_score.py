#!/usr/bin/env python3
"""
GPT Score Evaluation using a different LLM to assess the multi-agent system's performance
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import numpy as np
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from core.config import settings

class GPTScoreEvaluator:
    """
    Evaluates the quality of multi-agent responses using Claude
    Metrics:
    - Coherence (0.25): Evaluates response structure and logic
    - Relevance (0.30): Measures how well response matches query intent
    - Context Awareness (0.25): Assesses context maintenance
    - Consistency (0.20): Checks information and recommendation consistency
    """
    
    def __init__(self):
        self.orchestrator = MultiAgentTravelOrchestrator()
        self.evaluator_llm = ChatAnthropic(
            model=settings["models"]["claude_evaluator"],
            temperature=0
        )
        
        # Load evaluation prompts
        self.load_evaluation_prompts()
        
    def load_evaluation_prompts(self):
        """Load evaluation prompts for each metric"""
        self.evaluation_prompts = {
            "coherence": ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are a language expert evaluating the coherence of responses.
                Score from 0-10 based on:
                1. Complete and well-structured sentences
                2. Logical flow of information
                3. Clear topic transitions
                4. Natural language use
                Return only the numeric score."""),
                HumanMessage(content="Query: {query}\nResponse: {response}")
            ]),
            
            "relevance": ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are evaluating how relevant a response is to the query.
                Score from 0-10 based on:
                1. Direct answer to the question
                2. Appropriate intent matching
                3. Information accuracy
                4. Appropriate level of detail
                Return only the numeric score."""),
                HumanMessage(content="Query: {query}\nIntent: {intent}\nResponse: {response}")
            ]),
            
            "context_awareness": ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are evaluating context awareness in a conversation.
                Score from 0-10 based on:
                1. Maintenance of conversation context
                2. Appropriate reference resolution
                3. Use of previously mentioned information
                4. Smooth context transitions
                Return only the numeric score."""),
                HumanMessage(content="Previous Context: {context}\nCurrent Query: {query}\nResponse: {response}")
            ]),
            
            "consistency": ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are evaluating response consistency in recommendations.
                Score from 0-10 based on:
                1. Consistent information across responses
                2. Aligned recommendations
                3. Stable preferences handling
                4. Reliable facts and details
                Return only the numeric score."""),
                HumanMessage(content="Previous Responses: {prev_responses}\nCurrent Response: {response}")
            ])
        }

    def evaluate_conversation(self, conversation: List[Dict]) -> Dict[str, float]:
        """Evaluate a complete conversation"""
        scores = {
            "coherence": [],
            "relevance": [],
            "context_awareness": [],
            "consistency": []
        }
        
        previous_responses = []
        conversation_context = ""
        
        for turn in conversation:
            query = turn["query"]
            response = turn["response"]
            intent = turn.get("intent", "")
            
            # Evaluate each metric
            try:
                # Coherence
                coherence_response = self.evaluator_llm.invoke(
                    self.evaluation_prompts["coherence"].format_messages(
                        query=query, response=response
                    )
                )
                scores["coherence"].append(float(coherence_response.content))
                
                # Relevance
                relevance_response = self.evaluator_llm.invoke(
                    self.evaluation_prompts["relevance"].format_messages(
                        query=query, intent=intent, response=response
                    )
                )
                scores["relevance"].append(float(relevance_response.content))
                
                # Context Awareness
                context_response = self.evaluator_llm.invoke(
                    self.evaluation_prompts["context_awareness"].format_messages(
                        context=conversation_context, query=query, response=response
                    )
                )
                scores["context_awareness"].append(float(context_response.content))
                
                # Consistency
                if previous_responses:
                    consistency_response = self.evaluator_llm.invoke(
                        self.evaluation_prompts["consistency"].format_messages(
                            prev_responses="\n".join(previous_responses), response=response
                        )
                    )
                    scores["consistency"].append(float(consistency_response.content))
                
                # Update context and previous responses
                conversation_context += f"Q: {query}\nA: {response}\n"
                previous_responses.append(response)
                
            except Exception as e:
                print(f"Error evaluating turn: {e}")
                continue
        
        # Calculate final scores
        final_scores = {}
        weights = {
            "coherence": 0.25,
            "relevance": 0.30,
            "context_awareness": 0.25,
            "consistency": 0.20
        }
        
        for metric, values in scores.items():
            if values:
                final_scores[metric] = np.mean(values)
            else:
                final_scores[metric] = 0.0
                
        # Calculate weighted GPT Score
        gpt_score = sum(score * weights[metric] 
                       for metric, score in final_scores.items())
        final_scores["gpt_score"] = gpt_score
        
        return final_scores

def run_gpt_score_evaluation():
    """Run GPT Score evaluation on test conversations"""
    print("🚀 Starting GPT Score Evaluation")
    print("=" * 80)
    
    # Test conversations
    test_conversations = [
        # Basic travel planning conversation
        [
            {
                "query": "Tôi muốn đi Đà Lạt 3 ngày",
                "response": "Tôi sẽ giúp bạn lập kế hoạch cho chuyến đi Đà Lạt 3 ngày...",
                "intent": "plan"
            },
            {
                "query": "Có nhà hàng ngon không?",
                "response": "Ở Đà Lạt có nhiều nhà hàng ngon...",
                "intent": "eat"
            }
        ],
        # Complex booking scenario
        [
            {
                "query": "Đặt khách sạn ở Hội An",
                "response": "Tôi sẽ tìm khách sạn phù hợp ở Hội An cho bạn...",
                "intent": "book"
            },
            {
                "query": "Gần phố cổ nhé",
                "response": "Tôi đã tìm được một số khách sạn gần phố cổ...",
                "intent": "book"
            }
        ]
    ]
    
    evaluator = GPTScoreEvaluator()
    all_scores = []
    
    for i, conversation in enumerate(test_conversations, 1):
        print(f"\n📝 Evaluating Conversation {i}:")
        print("-" * 40)
        
        scores = evaluator.evaluate_conversation(conversation)
        all_scores.append(scores)
        
        print("\n📊 Scores:")
        for metric, score in scores.items():
            print(f"{metric.replace('_', ' ').title()}: {score:.2f}")
    
    # Calculate average scores
    avg_scores = {}
    for metric in all_scores[0].keys():
        avg_scores[metric] = np.mean([s[metric] for s in all_scores])
    
    print("\n📈 Overall Average Scores:")
    print("-" * 40)
    for metric, score in avg_scores.items():
        print(f"{metric.replace('_', ' ').title()}: {score:.2f}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        "individual_conversations": all_scores,
        "average_scores": avg_scores
    }
    
    filename = f"gpt_score_results_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to {filename}")

if __name__ == "__main__":
    run_gpt_score_evaluation()