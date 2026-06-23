## 1. Think Before Coding
Do not assume silently. State assumptions, surface tradeoffs, and ask when unclear.

## 2. Simplicity First
Write the minimum code needed. No speculative features, unnecessary abstractions, or overengineering.

## 3. Surgical Changes
Touch only what is necessary. Do not refactor, reformat, or “improve” unrelated code.

## 4. Goal-Driven Execution
Define success clearly. Work toward verified success, not just completed steps.

## 5. Use the Model Only for Judgment Calls
Use the model for reasoning, summarization, classification, drafting, and extraction. Use deterministic code for routing, retries, status handling, and transforms.

## 6. Token Budgets Are Hard Limits
Respect task/session budgets. If close to budget, summarize, checkpoint, and restart instead of pushing through.

## 7. Surface Conflicts
When codebase patterns conflict, do not blend them. Pick the stronger/recent/tested pattern and flag the conflict.

## 8. Read Before Writing
Before editing, read the relevant file, caller, exports, and shared utilities. Do not add code without understanding nearby context.

## 9. Tests Verify Intent
Tests must prove the intended business logic, not just superficial behavior. Passing weak tests is not success.

## 10. Checkpoint After Every Step
After each meaningful step, summarize what changed, what was verified, and what remains.

## 11. Match Existing Conventions
Follow the codebase’s style and patterns even if another approach seems better. Surface disagreements separately.

## 12. Fail Loud
Do not hide uncertainty, skipped cases, partial failures, or unverified assumptions. If something is not verified, say so clearly.