"""AI integration layer — where generative + agentic AI plugs in.

Design principle (the same one Odoo itself is moving toward with its
AI features): the AI never talks to the database directly. It produces
STRUCTURED decisions (tool calls), and the normal business logic in
`services/` + `models/` executes them. That keeps the AI testable and
the core business logic AI-free.
"""
