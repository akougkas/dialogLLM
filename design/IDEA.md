# DialogueLLM - Product Requirements Document

## 1. Introduction

DialogueLLM is a system designed to facilitate continuous conversations between two Large Language Models (LLMs). This project focuses on establishing a robust communication framework using a queuing system, enabling the exploration of dynamic interactions between LLMs.

## 2. Goals

*   Enable continuous, back-and-forth conversations between two LLMs with a conversation moderator in the middle.
*   Implement a queuing mechanism using Redis to manage message flow.
*   Establish a clients-server architecture for efficient communication.
*   Utilize the 'ollama' Python library for LLM interaction.
*   Integrate a larger LLM for conversation analysis, focusing on specific metrics.

## 3. Scope

This Minimum Viable Product (MVP) will focus on:

*   Setting up the communication infrastructure between the three LLMs.
*   Implementing the Redis queues for message management.
*   Developing the core Python application.
*   Ensuring the conversation runs for a continuous configurable duration.
*   Implementing basic analysis of the conversation log by the large LLM.

## 4. Functional Requirements

*   **Conversation Management:** The system must manage the flow of conversation, ensuring messages are delivered to the correct LLM and responses are received.
*   **Queue Management:** The system must utilize Redis queues (request and response) to handle message passing between LLMs.  Messages will remain in the queue until the manager removes them after the configurable conversation duration.
*   **LLM Interaction:** The 'ollama' library must be used to send prompts to and receive responses from the LLMs. Structured outputs must be utilized since there is no human in the loop.
*   **Initialization:** The large LLM will generate a story and two personas, providing an initial prompt to both smaller LLMs via their respective queues.
*   **Timer:** A timer must be implemented to control the conversation duration.
*   **Logging & Analysis:** The system must log the complete conversation. The large LLM will analyze the conversation based on metrics defined in the initial prompt, including sentiment, semantics, factual accuracy, privacy concerns, and other relevant factors.

## 5. Non-Functional Requirements

*   **Performance:** The system should be efficient in handling message passing and LLM interaction.
*   **Scalability:** The architecture should be designed with potential future scaling in mind (adding more LLMs).
*   **Maintainability:** The codebase should be well-structured and documented for easy maintenance.

## 6. Technical Design

*   **Architecture:** Client-server
*   **Programming Language:** Python
*   **LLM Interaction Library:** 'ollama'
*   **Queueing System:** Redis
*   **Deployment:** The large LLM (manager) will run on a desktop computer. The two smaller LLMs will run on separate servers.

## 7. Future Considerations

*   Scalability to support more than two LLMs.
*   Enhanced logging and data analysis capabilities.
*   More sophisticated analysis metrics and reporting.

## 8. Considerations

*   **Specific metrics for conversation analysis:** While categories are defined (sentiment, semantics, etc.), the exact metrics for each need to be precisely defined in the initial prompt generation by the large LLM.  This needs to be standardized.
*   **Format of the conversation log:**  The format in which the conversation log is stored (e.g., JSON, plain text) needs to be determined.  This will influence the analysis process.
*   **Error Handling:** The system should include robust error handling to manage potential issues with LLM communication, queue access, and other system failures.  This should be specified.