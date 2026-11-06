# content.py: everything participants read. Edit wording here, not in the code.

# The same five ideas for everyone (UK side businesses that can run next to a job). Deliberately no money figures.
IDEAS = [
    {"name": "Mobile bike repair", "what": "Fix and service bikes at customers' homes or workplaces in the evenings and at weekends."},
    {"name": "Meal prep for busy people", "what": "Cook healthy meals in batches once a week for busy professionals and families, delivered or collected."},
    {"name": "Bookkeeping for small businesses", "what": "Do the monthly bookkeeping and invoicing for sole traders and very small firms, remotely, a few hours a week."},
    {"name": "Pet sitting and dog walking", "what": "Look after pets and walk dogs for owners who are at work or away, in your neighbourhood."},
    {"name": "Personalised gifts online", "what": "Make personalised gifts (prints, mugs, cards) to order and sell them through an online marketplace."},
]
# Everyone works on the same idea (1-based position in the list above). Set ASSIGNED_IDEA in Render to change it.
DEFAULT_ASSIGNED_IDEA = 4

# The slide: a Business Model Canvas adapted to a side business that runs next to a main job.
# `hybrid` marks the boxes that are specific to side businesses (shown with a small label).
BLOCKS = [
    {"key": "customers", "title": "Customers and their problem", "hint": "Who will pay you, and what do they struggle with?", "hybrid": False},
    {"key": "offer", "title": "Your offer", "hint": "What exactly do you sell or do for them?", "hybrid": False},
    {"key": "channels", "title": "How customers find you", "hint": "Where do they hear about you and how do they book or buy?", "hybrid": False},
    {"key": "edge", "title": "Why you", "hint": "Your skills, experience or story that make customers choose you.", "hybrid": False},
    {"key": "time", "title": "Time and fit with your main job", "hint": "How many hours a week, when, and how it works around your job.", "hybrid": True},
    {"key": "resources", "title": "What you need", "hint": "Tools, equipment, skills, helpers or partners.", "hybrid": False},
    {"key": "income", "title": "Money in", "hint": "What you charge and how often customers pay.", "hybrid": False},
    {"key": "costs", "title": "Money out", "hint": "Start-up and running costs.", "hybrid": False},
    {"key": "steps", "title": "First 30 days", "hint": "The first steps you would take, in order.", "hybrid": True},
]
BLOCK_KEYS = [b["key"] for b in BLOCKS]
MIN_FILLED_BOXES = 5      # the slide can only be handed in once this many boxes have text
MAX_BOX_CHARS = 600

TEXT = {
    "intro_title": "Your side-business slide",
    "intro_lead": ("Here are five side-business ideas that people can run next to a main job. "
                   "Everyone in this study sees the same five ideas."),
    "intro_task": ("Your task: design a one-slide business model canvas for idea {n}, {name}. It shows, on one page, "
                   "how the side business would work next to a main job. Fill in the boxes and give your business a name."),
    "intro_ai": ("While you work, an AI co-founder is available in the panel beside the slide. You can ask it for "
                 "ideas, questions or feedback, and you decide what goes on the slide."),
    "intro_noai": "You will work on the slide on your own.",
    "intro_time": "You have {minutes} minutes. The slide is saved automatically while you work.",
    "start": "Start",
    "canvas_title": "Side-business canvas",
    "your_idea": "Your idea",
    "name_label": "Name of your side business",
    "name_placeholder": "Give it a name",
    "hybrid_label": "Hybrid",
    "submit": "Hand in my slide",
    "saved": "Saved",
    "need_more": "Please fill in at least {n} boxes before you hand in your slide.",
    "confirm_title": "Hand in your slide?",
    "confirm_text": "You cannot change it afterwards.",
    "confirm_yes": "Yes, hand in",
    "confirm_no": "Keep working",
    "timeup": "Time is up. Your slide has been handed in.",
    "done_title": "Thank you",
    "done_text": "Your slide has been saved. You can now continue with the survey.",
    "done_button": "Continue",
    "ai_title": "AI co-founder",
    "ai_opening": ("Hi, I'm your AI co-founder. I can help you think through any box on your slide: who your customers "
                   "are, what to charge, how it fits around your job. Which box would you like to start with?"),
    "ai_placeholder": "Write your message…",
    "ai_error": "Sorry, I'm having trouble right now. Please try again in a moment.",
    "ai_disclaimer": "Your conversation is recorded for research purposes. Please don't share your name, address or employer. The AI can make mistakes.",
    "notice": "Your answers are recorded for research purposes. Please don't share your name, address or employer.",
}
