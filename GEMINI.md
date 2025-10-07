
# Gemini Code Assistant Guidelines

This document outlines the core principles, architectural considerations, and technical constraints for all code changes and contributions managed by the Gemini Code Assistant. Adherence to these guidelines is mandatory for all code generations and Pull Request Proposals (PRPs).

## 1. Architectural Context

The Code Assistant will derive its understanding of the application from the following sources:

| Resource | Purpose |
| :--- | :--- |
| **`README.md`** | **Application Logic:** Contains the high-level description, feature set, and operational logic of the application. This is the primary source for understanding *what* the application does. |
| **`ddl_postgres.sql`** | **SQL Schema:** Defines the complete database structure, including tables, columns, relationships, and constraints. This is the primary source for understanding the *data model*. |

---

## 2. Core Development Principles

You **MUST** follow these principles in all design decisions, code implementations, and PRP generations:

### 2.1. KISS (Keep It Simple, Stupid)
* **Simplicity** is paramount. Design solutions to be as straightforward as possible.
* Always favor the simplest, most **direct implementation** that satisfies the requirement.
* Avoid clever or overly optimized code that sacrifices clarity. Simple code is inherently easier to understand, maintain, and debug.

### 2.2. YAGNI (You Aren't Gonna Need It)
* **Implement only what is necessary** to meet the current requirements.
* **Avoid speculative implementation**—do not add features, configuration, or abstraction layers based on an *anticipation* of future need.
* Focus on solving the problem at hand, not future, hypothetical problems.

### 2.3. Open/Closed Principle (OCP)
* **Open for Extension:** The design should allow new functionality to be added (extended) without requiring changes to the existing, stable codebase.
* **Closed for Modification:** Once a module or class is working and stable, it should ideally not need to be modified when introducing new features.
* Achieve this through **interfaces, abstract classes, and composition** rather than inheritance or direct modification of core logic.

### 2.4. Liskov Substitution Principle (LSP)
* Objects of a superclass should be replaceable with objects of its subclasses without breaking the application. 
* Subclasses must adhere to the contract of their base class.

---

## 3. Technical Constraints

### 3.1. Language and Environment
* **Coding Language:** **Python 3.10**

### 3.2. Dependencies and Libraries
* **Existing Libraries:** Prioritize the use of libraries and specific versions already listed in **`requirements.txt`**.
* **External Libraries:** **Do not introduce new libraries** unless it is absolutely necessary (i.e., the required functionality cannot be reasonably achieved with Python's standard library or existing dependencies).

### 3.3. Code Quality and Typing
* **Type Hints:** **Always use type hints** for function arguments, return values, and variable assignments.
* **Typing Library:** Use the **`typing`** standard library module for complex or advanced type hints (e.g., `Union`, `Optional`, `List`, `Dict`, `Generic`).