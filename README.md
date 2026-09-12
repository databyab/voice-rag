# Pipecat + RAG Conversational AI Assistant

A hands-on project exploring **Pipecat and Voice AI** by integrating a voice layer into an existing Retrieval-Augmented Generation (RAG) application.

The goal was to understand how a text-based RAG application can be extended to support voice interaction using real-time audio pipelines.

## Overview

The application supports two interaction modes:

```text
                    React Frontend
                          |
                +---------+---------+
                |                   |
              Chat                Voice
                |                   |
                |                Pipecat
                |                   |
                +---------+---------+
                          |
                     RAG Service
                          |
                      Retriever
                          |
                       ChromaDB
                          |
                    Context Builder
                          |
                       Groq LLM
                          |
                     Response
```

## Voice Pipeline

The main focus of this project is experimenting with Pipecat and understanding how the different components of a voice application connect.

```text
Browser Microphone
        |
    Audio Stream
        |
      Pipecat
        |
      Whisper
       STT
        |
 Transcribed Text
        |
    RAG Service
        |
     Groq LLM
        |
 Generated Response
        |
    Edge-TTS
       TTS
        |
   Audio Stream
        |
      Browser
```

## Tech Stack

* Pipecat — real-time voice pipeline
* Groq — LLM inference
* Whisper — speech-to-text
* Edge-TTS — text-to-speech
* Sentence Transformers — local embeddings
* ChromaDB — vector database
* FastAPI — backend
* React + Vite — frontend

## RAG Layer

The existing RAG system uses:

* `sentence-transformers/all-MiniLM-L6-v2` for embeddings
* ChromaDB for persistent local vector storage
* `pypdf` for PDF processing
* `python-docx` for Word documents
* Markdown and text document support
* Groq for response generation

The RAG flow is:

```text
User Query
    |
Query Embedding
    |
ChromaDB Search
    |
Relevant Chunks
    |
Context + Conversation History
    |
Groq LLM
    |
Response
```

## What I'm Learning With Pipecat

The main purpose of this project is to understand how Pipecat can be used to build real-time conversational systems.

I'm currently exploring:

* Pipecat pipeline architecture
* Audio streaming
* STT and TTS integration
* Connecting voice input to an existing RAG pipeline
* Response streaming
* Turn-taking
* Interruptions
* Latency in voice interactions
* Managing conversational state

## Current State

This is still a learning project rather than a fully autonomous voice agent.

Currently, the user manually starts the voice mode, speaks, waits for the response, and manually interrupts when needed.

The next step is to make the interaction more natural by working on:

* Better interruption handling
* Continuous conversation
* Turn detection
* Voice activity detection
* Lower-latency STT/TTS
* More natural conversational flow

The interesting part for me is understanding what changes when a traditional RAG application moves from text interaction to real-time voice interaction.

