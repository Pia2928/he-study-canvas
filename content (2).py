# content.py: everything participants read. Edit wording here, not in the code.

# The same five ideas for everyone: UK side businesses that fit university students and people with a main job.
# Deliberately no money figures.
IDEAS = [
    {"name": "Tutoring", "what": "Teach GCSE, A-level or university-level subjects to pupils and students, online or in your area, in the evenings and at weekends."},
    {"name": "Social media for local businesses", "what": "Plan, film and post content for small local businesses (cafes, salons, gyms) that don't have the time to do it themselves."},
    {"name": "Reselling on Vinted and eBay", "what": "Find second-hand clothes, trainers or gadgets (charity shops, car boot sales, your own wardrobe) and resell them online at a profit."},
    {"name": "Dog walking and pet sitting", "what": "Walk dogs and look after pets for owners who are at work or away, in your neighbourhood."},
    {"name": "Personalised gifts and prints", "what": "Make custom gifts, prints or cards to order and sell them through an online marketplace such as Etsy."},
]
# Everyone works on the same idea (1-based position in the list above). Set ASSIGNED_IDEA in Render to change it.
DEFAULT_ASSIGNED_IDEA = 3

# The slide: a Business Model Canvas adapted to a side business next to studies or a job. The boxes unlock one by one.
# `hybrid` marks the boxes that are specific to side businesses.
EXAMPLE_BUSINESS = "a mobile car-valeting business"
BLOCKS = [
    {"key": "customers", "title": "Your customers", "hybrid": False,
     "question": "Who will pay you, and what problem do you solve for them?",
     "tips": ["Think of one specific type of person, not everyone.", "What are they struggling with or short of?",
              "Where do they live or spend their time?"],
     "example": "Busy professionals in my town who never find time to clean their car, mainly at weekends."},
    {"key": "offer", "title": "What you offer", "hybrid": False,
     "question": "What exactly do customers get from you?",
     "tips": ["What do they receive, and what changes for them?", "How is it different from what they can already buy?",
              "Can you describe it in one sentence?"],
     "example": "A 90-minute inside-and-out clean at the customer's home, with a before and after photo."},
    {"key": "channels", "title": "How they find you", "hybrid": False,
     "question": "How do customers hear about you, and how do they book or buy?",
     "tips": ["Where do your customers already spend time, online or locally?", "How would they first hear about you?",
              "How do they pay or book?"],
     "example": "Local Facebook groups, leaflets in apartment blocks and word of mouth. Customers book by text message."},
    {"key": "edge", "title": "Why you", "hybrid": False,
     "question": "Why would customers choose you over someone else?",
     "tips": ["What skills, hobbies or experience do you already have?", "What makes you more trustworthy or better than a stranger?",
              "Is there anything people can check, such as reviews, a degree or a reputation?"],
     "example": "I worked in a car wash for two summers. I'm quick, careful and always on time."},
    {"key": "time", "title": "Your time", "hybrid": True,
     "question": "How does this fit around your studies or your main job?",
     "tips": ["How many hours a week can you realistically give?", "Which days or times work around lectures or work?",
              "What happens in a busy week?"],
     "example": "5 hours a week: Saturday mornings and one weekday evening, never during lectures or work."},
    {"key": "resources", "title": "What you need", "hybrid": False,
     "question": "Which tools, skills or people do you need to get started?",
     "tips": ["What equipment or software do you need?", "What do you already own?",
              "Is there someone who could help or lend you something?"],
     "example": "A bucket, microfibre cloths, a small vacuum and car-safe products. A friend lends me a hose."},
    {"key": "income", "title": "Money in", "hybrid": False,
     "question": "What do you charge, and how do customers pay?",
     "tips": ["What will you charge, and per what (hour, item, month)?", "How many customers would you need each month?",
              "When do customers pay you?"],
     "example": "£30 per clean, paid by bank transfer after the job. Eight cleans a month is the first goal."},
    {"key": "costs", "title": "Money out", "hybrid": False,
     "question": "What does it cost to start and to keep going?",
     "tips": ["What do you have to buy before you start?", "Which costs come back every month?",
              "What is the cheapest way to get going?"],
     "example": "About £60 of supplies to start, then roughly £15 a month for products and fuel."},
    {"key": "steps", "title": "First 30 days", "hybrid": True,
     "question": "What are the first steps you would take, in order?",
     "tips": ["What is the very first thing you would do this week?", "What could you test before spending money?",
              "Who could be your first customer?"],
     "example": "Week 1: clean three friends' cars for free and take photos. Week 2: post the photos locally and set a price."},
]
BLOCK_KEYS = [b["key"] for b in BLOCKS]
BLOCK_BY_KEY = {b["key"]: b for b in BLOCKS}
MIN_WORDS_TO_UNLOCK = 3   # a box must have this many words before the next box unlocks
MIN_FILLED_BOXES = 5      # the slide can only be handed in once this many boxes have text
MAX_BOX_CHARS = 600
THEMES = [
    {"key": "indigo", "name": "Indigo", "color": "#4f46e5"},
    {"key": "teal", "name": "Teal", "color": "#0f766e"},
    {"key": "rose", "name": "Rose", "color": "#be123c"},
    {"key": "amber", "name": "Amber", "color": "#b45309"},
    {"key": "slate", "name": "Slate", "color": "#334155"},
]
THEME_KEYS = [t["key"] for t in THEMES]

TEXT = {
    "intro_title": "Build your side-business slide",
    "intro_lead": ("Here are five side-business ideas that suit people who study or work and want to earn some extra money. "
                   "Everyone in this study sees the same five ideas."),
    "intro_task": ("Your task: build a one-slide business plan for idea {n}, {name}. You will work through nine boxes one "
                   "by one. Each box you complete unlocks the next, and at the end you have a slide you can customise "
                   "with your own business name and colour."),
    "intro_ai": ("An AI co-founder works with you the whole way. Every time you open a box it suggests ideas, and you can "
                 "reply, ask questions and shape them. You decide what goes on the slide."),
    "intro_noai": "You will build the slide on your own. Each box comes with questions and an example to guide you.",
    "intro_time": "You have {minutes} minutes. Your slide is saved automatically while you work.",
    "start": "Start building",
    "canvas_title": "Side-business slide",
    "your_idea": "Your idea",
    "banner_ai": "Your AI co-founder is ready. Open a box and it will suggest ideas. Reply to shape them, then make them yours.",
    "banner_noai": "Work through the boxes one by one. Each box you complete unlocks the next.",
    "name_label": "Business name",
    "name_placeholder": "Give your business a name",
    "tagline_label": "One-line pitch",
    "tagline_placeholder": "What does your business do, in one sentence?",
    "colour_label": "Slide colour",
    "preview": "Preview slide",
    "preview_title": "Your slide",
    "close": "Close",
    "hybrid_label": "Side business",
    "progress": "{n} of {total} boxes done",
    "locked": "Unlocks after \"{prev}\"",
    "empty_box": "Click to start",
    "editor_placeholder": "Write your answer here…",
    "editor_hint": "At least {n} words to continue",
    "done_next": "Done, next box",
    "done_last": "Done, preview my slide",
    "unlocked": "Box unlocked: {name}",
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
    "ai_opening": ("Hi, I'm your AI co-founder. We'll build your slide box by box. Open the first box, and I'll suggest "
                   "some ideas to start from. You can reply to me at any time."),
    "ai_placeholder": "Reply to your co-founder…",
    "ai_thinking": "Thinking of suggestions for \"{box}\"…",
    "ai_for_box": "Suggestions for \"{box}\"",
    "ai_use": "Add to my box",
    "ai_used": "Added",
    "ai_quick_more": "More suggestions",
    "ai_quick_feedback": "Give me feedback",
    "ai_error": "Sorry, I'm having trouble right now. Please try again in a moment.",
    "ai_disclaimer": "Your conversation is recorded for research purposes. Please don't share your name, address or employer. The AI can make mistakes.",
    "guide_title": "Guide",
    "guide_think": "Things to think about",
    "guide_example": "Example, for {name}",
    "notice": "Your answers are recorded for research purposes. Please don't share your name, address or employer.",
}
