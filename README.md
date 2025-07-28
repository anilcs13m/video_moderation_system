# Video Moderation Service for Short-Form Platform

A comprehensive AI-powered video moderation system for short-form video platforms, that performs multiple checks in parallel to ensure content safety and quality. The system performs multi-stage parallel processing to analyze video content across multiple dimensions including safety, legal compliance, quality, and content similarity.
## Features

- **Multi-stage AI Moderation**
  - NSFW Content Detection :- use I3D features for content detection
  - Copyright Violation Detection :- performs vector similarity for matching against known copyrighted content
  - Object & Logo Recognition:- YOLO model for object detection
  - Text Extraction (OCR) :- Analyses text content on video frames
  - Video & Audio Quality Assessment :- Audio/Video Quality using NIMA and audio features
  - Content Similarity Check :- Identifies similar content using I3D features vectors
  - Business Rule Validation :- Define few rules for rejections

- **Smart Thumbnail Generation**
  - Face detection 
  - Emotion analysis
  - Quality-based selection

- **Scalable Architecture**
  - Parallel processing pipeline
  - FAISS vector database for similarity search
  - Elasticsearch integration

- ** Output and Decision Making**
  - Moderation Status: APPROVED, REJECTED, or FLAGGED
  - Moderation Level: HIGH, MEDIUM, or LOW risk assessment
  - Detailed Reports:

