# content.py: everything participants read. Edit wording here, not in the code.

# The same five ideas for everyone: UK side businesses that fit university students and people with a main job.
# Deliberately no money figures.
IDEAS = [
    {"name": "Dog walking and pet sitting", "what": "Walk dogs and look after pets for owners who are at work or away, in your neighbourhood, around your own shifts or lectures."},
    {"name": "Odd jobs and flat-pack assembly", "what": "Help neighbours and busy people with flat-pack furniture, hanging shelves, garden tidying and small repairs, booked by message."},
    {"name": "Reselling on Vinted and eBay", "what": "Find second-hand clothes, trainers or gadgets (charity shops, car boot sales, your own wardrobe) and resell them online at a profit."},
    {"name": "Online help for small businesses", "what": "Small businesses such as cafes, salons, tradespeople and online shops are too busy for office tasks. From home, in the hours you choose, you could answer their emails and messages, manage bookings, update spreadsheets or their online shop, or post on their Instagram and Facebook. You are paid per task or per hour."},
    {"name": "Tutoring and homework help", "what": "Help school pupils with homework, reading or maths, or practise English with learners, online or at home, outside school hours."},
]
# Everyone works on the same idea (1-based position in the list above). Set ASSIGNED_IDEA in Render to change it.
DEFAULT_ASSIGNED_IDEA = 3

# The slide: a Business Model Canvas adapted to a side business next to studies or a job. The boxes unlock one by one.
# `hybrid` marks the boxes that are specific to side businesses.
EXAMPLE_BUSINESS = "a mobile bike-repair business"
BLOCKS = [
    {"key": "customers", "title": "Your customers", "hybrid": False,
     "question": "Who will pay you, and what problem do you solve for them?",
     "tips": ["Think of one specific type of person, not everyone.", "What are they struggling with or short of?",
              "Where do they live or spend their time?"],
     "example": "Commuters and students in my area whose bikes need small repairs but who have no time to visit a shop."},
    {"key": "offer", "title": "What you offer", "hybrid": False,
     "question": "What exactly do customers get from you?",
     "tips": ["What do they receive, and what changes for them?", "How is it different from what they can already buy?",
              "Can you describe it in one sentence?"],
     "example": "Fixing punctures, brakes and gears at the customer's door in about 30 minutes, with a clear price list."},
    {"key": "channels", "title": "How they find you", "hybrid": False,
     "question": "How do customers hear about you, and how do they book or buy?",
     "tips": ["Where do your customers already spend time, online or locally?", "How would they first hear about you?",
              "How do they pay or book?"],
     "example": "Local Facebook groups, flyers in student halls and word of mouth. Customers book by text message."},
    {"key": "edge", "title": "Why you", "hybrid": False,
     "question": "Why would customers choose you over someone else?",
     "tips": ["What skills, hobbies or experience do you already have?", "What makes you more trustworthy or better than a stranger?",
              "Is there anything people can check, such as reviews, a degree or a reputation?"],
     "example": "I've fixed my own bikes for years, and I'm quick, tidy and fair on price."},
    {"key": "time", "title": "Your time", "hybrid": True,
     "question": "How does this fit around your studies or your main job?",
     "tips": ["How many hours a week can you realistically give?", "Which days or times work around lectures or work?",
              "What happens in a busy week?"],
     "example": "6 hours a week, on my days off and one evening, planned around my shifts."},
    {"key": "resources", "title": "What you need", "hybrid": False,
     "question": "Which tools, skills or people do you need to get started?",
     "tips": ["What equipment or software do you need?", "What do you already own?",
              "Is there someone who could help or lend you something?"],
     "example": "A basic tool kit, a puncture repair kit and a few common spare parts. A pump from my own garage."},
    {"key": "income", "title": "Money in", "hybrid": False,
     "question": "What do you charge, and how do customers pay?",
     "tips": ["What will you charge, and per what (hour, item, month)?", "How many customers would you need each month?",
              "When do customers pay you?"],
     "example": "A flat fee per job plus parts at cost, paid by bank transfer or cash after the job."},
    {"key": "costs", "title": "Money out", "hybrid": False,
     "question": "What does it cost to start and to keep going?",
     "tips": ["What do you have to buy before you start?", "Which costs come back every month?",
              "What is the cheapest way to get going?"],
     "example": "About £80 for tools and parts to start, then small top-ups when spare parts run out."},
    {"key": "steps", "title": "First 30 days", "hybrid": True,
     "question": "What are the first steps you would take, in order?",
     "tips": ["What is the very first thing you would do this week?", "What could you test before spending money?",
              "Who could be your first customer?"],
     "example": "Week 1: fix three friends' bikes for free and take photos. Week 2: post the photos locally and set a price list."},
]
BLOCK_KEYS = [b["key"] for b in BLOCKS]
ICONS = {"customers": "\U0001F465", "offer": "\U0001F381", "channels": "\U0001F4E3", "edge": "\u2B50", "time": "\u23F0",
         "resources": "\U0001F6E0\uFE0F", "income": "\U0001F4B7", "costs": "\U0001F9FE", "steps": "\U0001F680"}
for _b in BLOCKS:
    _b["icon"] = ICONS.get(_b["key"], "")

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
    "intro_title": "Design your own side business",
    "intro_lead": ("You now have time to turn an idea into a real plan. Below are five side businesses that people "
                   "in the UK can start next to studying or a main job, including shift work, with little money and "
                   "flexible hours. The best way to develop an idea is to brainstorm it step by step. "
                   "To begin, choose the idea you would like to work on."),
    "intro_choose": "Tap an idea to choose it",
    "intro_chosen": "Your choice",
    "intro_task": ("You chose {name}. Now design your own business around it. You will work through nine short boxes "
                   "that cover everything worth thinking about: your customers, what you offer, how they find you, "
                   "your money and your first steps. Each box you complete unlocks the next, and at the end you "
                   "have a one-slide business plan with your own business name, pitch and colour."),
    "intro_ai": ("An AI co-founder works with you the whole way. Each time you open a box it shares suggestions and "
                 "asks you questions, and you can reply, ask for ideas or ask for feedback. You decide what goes on "
                 "the slide."),
    "intro_noai": ("You will build the slide on your own. Each box comes with guiding questions, tips and an example "
                   "to help you brainstorm."),
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
    "all_done": "All nine boxes done. Preview your slide, then hand it in.",
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
    "ai_back_to": "Back to \"{box}\"",
    "ai_new": "Your co-founder has new suggestions",
    "tab_ai": "Co-founder",
    "tab_guide": "Guide",
    "tab_write": "Write",
    "tab_slide": "Slide",
    "intro_next": "Next",
    "intro_back": "Back",
    "intro_ideas_title": "Five ideas",
    "intro_task_title": "Your task",
    "ai_error": "Sorry, I'm having trouble right now. Please try again in a moment.",
    "ai_disclaimer": "Your conversation is recorded for research purposes. Please don't share your name, address or employer. The AI can make mistakes.",
    "guide_title": "Guide",
    "guide_think": "Things to think about",
    "guide_example": "Example, for {name}",
    "notice": "Your answers are recorded for research purposes. Please don't share your name, address or employer.",
}
