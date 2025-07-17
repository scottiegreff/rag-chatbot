# AI Chatbot Performance Test Report

**Test Date:** 2025-07-16 11:24:20  
**Test ID:** 2025-07-16_11-24-20  
**Model:** Mistral 7B Instruct v0.2 (Q4_K_M quantization)  
**Hardware:** Apple M1 Mac  

---

## Test Configuration

| **Component** | **M1 GPU (Local)** | **Docker CPU** |
|---------------|-------------------|----------------|
| **Environment** | Native macOS with Metal | Docker container |
| **GPU Layers** | 4 (Metal acceleration) | 4 (containerized) |
| **Memory Access** | Direct Metal API | Virtualized container |

---

## Performance Results

### M1 GPU (Local) Results


### Docker CPU Results

**Environment:** Docker CPU
**Test Time:** 2025-07-16T11:23:39.054727

#### Simple Query

- **Total Time:** 16065.0ms
- **First Token Latency:** 14053.4ms
- **Generation Time:** 2011.6ms
- **Tokens Generated:** 9
- **Tokens/Second:** 4.47
- **Response Length:** 80 characters

**Response Preview:**  The capital of France is Paris, and it is located in the Île-de-France region.


#### Rag Query

- **Total Time:** 5947.1ms
- **First Token Latency:** 1771.1ms
- **Generation Time:** 4175.9ms
- **Tokens Generated:** 22
- **Tokens/Second:** 5.27
- **Response Length:** 232 characters

**Response Preview:**  Sure! Coady was a student of FCIA in her early years while Scott worked for the company as an engineer. They used to hang out together in their free time, playing video games, watching movies, or jus...

#### Sql Query

- **Total Time:** 8961.6ms
- **First Token Latency:** 6385.0ms
- **Generation Time:** 2576.7ms
- **Tokens Generated:** 12
- **Tokens/Second:** 4.66
- **Response Length:** 139 characters

**Response Preview:**  I do not have access to your database. However, according to the e-commercce database you provided, there are 40 products in the database.

#### Long Generation

- **Total Time:** 10733.2ms
- **First Token Latency:** 6665.8ms
- **Generation Time:** 4067.4ms
- **Tokens Generated:** 22
- **Tokens/Second:** 5.41
- **Response Length:** 271 characters

**Response Preview:**  Machine learning is the field that uses algorithms to improve and optimize data-driven models for predictive analysis. Examples include recommendation engines, image recognition, chatbots, and natura...

## Performance Comparison

| **Test Type** | **Metric** | **M1 GPU** | **Docker CPU** | **Performance Ratio** |
|---------------|------------|------------|----------------|---------------------|
## Key Findings

- **Docker CPU Performance:** Average 4.95 tokens/sec
- **M1 GPU Results:** Not available (environment switch failed)

## Recommendations

- **For Production:** Use M1 GPU with Metal acceleration for optimal performance
- **For Development:** Docker CPU provides consistent cross-platform compatibility
- **For Testing:** Use this script for ongoing performance monitoring
