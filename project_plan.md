# SeniorCare Friend Project Development Outline

## 1. Computer Vision Model for Face Recognition
- Develop the model to recognize multiple faces accurately.
- Estimate the number of photos/videos needed to fine-tune the model for each person.
- Set up automatic model retraining for new faces.

## 2. Build Database
- Define data models/schema.
- Configure table with patient information (timings of drug intake, appointments, etc.).
- Create table with assistant personal preferences per person (voice, attitude).
- Develop table with chat history per person.
- Establish table with system information (patient/caregiver accounts, credentials, etc.).

## 3. Run/Configure MQTT Service for Message Exchange
- ...

## 4. Create Assistant Manager Service for Task Management
- Define the scope of tasks.
- Implement task scheduling and prioritization logic.
- Integrate with other services through APIs.

## 5. Create Service for Response Personalization and General Queries
- Define user profiles and personalization parameters.
- Integrate with GPT/Bing for general querying.
- Ensure proper request handling.

## 6. Connect Necessary Smart Home Devices
- Create simple Home Automation (HA) Integration.
- Connect with Assistant Manager.

## 7. Create a Service for Reminders Handling
- ...

## 8. Create a Web/iOS/Android Graphical App
- Define core functionalities.
- Design UI/UX.

## 9. Set Up Text-To-Speech (TTS) Part
- Handle microphone input.
- Choose and integrate a TTS engine (like Whisper).
- Implement voice customization options.
- Optimize for natural-sounding speech.

## 10. Set Up Speech-To-Text (STT) Part (Speaker)
- Handle speaker output.
- Choose an STT service or library.
- Implement noise cancellation and voice activity detection.
- Optimize for accuracy and low latency.
- Integrate with the assistant manager for handling commands.

---

Each component is crucial to the seamless operation and user experience of the SeniorCare Friend system.
