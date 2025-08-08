# LLaMA Local Query Generator

## How to Run
1. Run the full setup and start all required services with a single command:

   ```bash
   make all
   ```

2. Open `main.ipynb`.

3. Select the proper virtual environment (already created automatically).
---

## Why We Use a Small Context Window and a Weak Model for Query Generation

When generating search queries, we deliberately use a weak model and a limited context window. Below is an explanation of why this approach was chosen.

### Limitations of a Weak Model

The model has limited capabilities, which makes obtaining high-quality and accurate answers for queries challenging. This is primarily because:

- **Local deployment requirement**  
  We aim to run everything locally without relying on powerful cloud services.

- **Why CPU?**  
  Running the model on a CPU simplifies setup and usage, avoiding the complexity of managing CUDA cores, toolkits, and other GPU-specific software. Different GPUs (AMD vs Nvidia) require different drivers and software versions, which complicates compatibility and maintenance.

- **Accessibility**  
  Using CPU ensures the solution is accessible to a wider audience since it can run on most PCs and laptops without specialized hardware.

### Why a Small Context Window is Needed

We limit the context window — the number of tokens available for processing and generating a response — for several reasons:

- **Minimizing "Garbage" in Outputs**  
  A small context window does not give the model enough "space" to generate unnecessary or irrelevant text. With a limited amount of input, the model cannot "dilute" the answer or insert unrelated information.

- **Increasing Speed**  
  Models with smaller context windows run faster, especially on CPUs. Although using the CPU is not ideal for performance, it allows the model to run smoothly on a wide range of hardware without additional dependencies.