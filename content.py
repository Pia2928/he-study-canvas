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
# One short line per idea, shown on the cards in "pitch" mode (UI_MODE=pitch).
for _i, _line in zip(IDEAS, ["Walk and look after pets while owners are at work.",
                             "Build flat-pack furniture and fix small things for neighbours.",
                             "Buy second-hand, resell online for a profit.",
                             "Handle messages and bookings for local businesses.",
                             "Help pupils with homework and exams."]):
    _i["line"] = _line
# Public UK facts the AI co-founder may quote (rounded; sources checked November 2026). Nothing else is quoted as a fact.
IDEA_FACTS = {
    "Dog walking and pet sitting": [
        "About 41% of UK households own a dog, roughly 15.5 million dogs, up from 33% in 2021 (UK Pet Food survey 2026).",
        "Reasoning, not a statistic: owners with long or irregular working hours, and flats in big cities, need walkers most."],
    "Odd jobs and flat-pack assembly": [
        "Taskrabbit's own UK data (a vendor, so treat as a guide): furniture assembly averages about £26 an hour, about £33 in London and about £36 in Edinburgh and Glasgow.",
        "Reasoning, not a statistic: renters, new movers and busy people in big cities pay for assembly because they lack tools or time."],
    "Reselling on Vinted and eBay": [
        "Vinted has roughly 17 million UK users (SpendMapper data) and its group revenue grew about 38% in 2025 to nearly £1bn.",
        "HMRC: the trading allowance is £1,000 a year before tax matters. Buying items to resell is more likely to count as trading than selling your own things. Platforms report accounts with 30+ sales or about 2,000 euros a year (MoneyHelper). Tell people to check gov.uk.",
        "Reasoning, not a statistic: big cities have more charity shops, student areas and buyers who collect in person, so stock is easier to find and sell."],
    "Online help for small businesses": [
        "The UK has about 5.6 million private businesses and about 4.1 million (74%) have no employees, so owners do their own admin (gov.uk 2026).",
        "Reasoning, not a statistic: cafes, salons, tradespeople and online shops lose time on messages, bookings and social media and will pay to hand it over."],
    "Tutoring and homework help": [
        "In England and Wales about 29% of secondary pupils have had private tuition, 45% in London against 27% in the rest of England; Year 11 is the busiest (Sutton Trust 2025).",
        "Parents pay about £24 an hour on average (Sutton Trust, survey year not stated)."],
}

# Concrete options the AI draws from when it suggests what to do, what to sell or what to charge. Prices are rough ranges
# from vendor pages (Airtasker, Checkatrade, MyBuilder, November 2026), so only a guide. Other lists are reasoning, not data.
IDEA_MENUS = {
    "Odd jobs and flat-pack assembly": [
        "Rough UK prices per job: TV mounting £100-200; flat-pack assembly £80-160 (about £20-35 an hour); putting up shelves £80-160; curtain rails £45-160; hanging pictures or mirrors £45-100; fixing doors or handles £70-130; regrouting or small tiling £150-300; gutter clean £30-50; garden tidy about £25 an hour.",
        "Handymen charge about £30 an hour on average and about £50 in London, and many set a £40-60 minimum call-out, so bundle small jobs into one visit.",
        "Best money for a beginner (reasoning): jobs paid per job that take 1-2 hours with few tools, such as TV mounting, shelves, curtain rails, mirrors, or a bed plus wardrobe in one visit. Weak: single small jobs and gutters (£30-50 for ladder work).",
        "Avoid as a beginner: electrics, gas and plumbing. They need qualifications and insurance, so tell them to check."],
    "Reselling on Vinted and eBay": [
        "Items people often resell (reasoning, not data): branded trainers (Nike, Adidas, New Balance), sportswear and outdoor jackets, vintage denim, kids' branded clothes, Lego sets, retro games. Where to find stock: car boot sales, charity shops in wealthier areas, house clearances, your own wardrobe.",
        "Profit rule: buy price + platform fees + postage + your time must leave a clear gain. Tell them to check each platform's current fees."],
    "Dog walking and pet sitting": [
        "Jobs to choose from (reasoning): midday walks for people working long hours, group walks of 2-4 dogs (more income per hour than single walks), puppy visits, drop-in feeding for cats, holiday stays at the owner's home. Tell them to check insurance and local council rules before taking several dogs."],
    "Online help for small businesses": [
        "Tasks owners hand over (reasoning): answering customer messages, managing bookings, updating opening hours and listings, posting on Instagram and Facebook, invoices in a spreadsheet, adding products to an online shop. Best first customers: salons, cafes and tradespeople near you, because they can be reached in person."],
    "Tutoring and homework help": [
        "Subjects and pupils to choose from (reasoning): GCSE maths and English (Year 11 is the busiest year), A-level maths and sciences, primary reading and maths, English practice for learners. Online sessions let you reach families in London and other big cities, where tuition is more common."],
}

# UK context the AI co-founder can draw on for ANY idea, including the participant's own. Names and rules only, no statistics
# except the HMRC allowance (checked November 2026). Tax, legal and licensing points are always "check it" (gov.uk).
UK_GENERAL = [
    "Where to find first customers in the UK (reasoning): go to where that customer group already spends time. Examples of channels, in no order: "
    "a neighbourhood app, a community or marketplace listing, a messaging group (halls, street, workplace), a noticeboard in a cafe, library or shop, "
    "a social media account, a second-hand or handmade marketplace, a trade or tutoring listing site, word of mouth. The channel must fit the customer, "
    "not the other way round.",
    "Taking bookings and payment (reasoning): a booking page such as Calendly or Google Calendar, a payment link (Stripe, PayPal, SumUp), bank transfer, "
    "WhatsApp Business auto-replies. Posting goods: Royal Mail, Evri, InPost lockers, Post Office drop-off.",
    "UK timing (reasoning): freshers' weeks in September and October, Christmas and Black Friday, the GCSE and A-level exam season in May and June, school holidays, "
    "bank holidays, the long summer break for students; evenings and weekends suit people with shifts.",
    "UK rules to mention only when relevant, always with 'check it on gov.uk': HMRC trading allowance of £1,000 a year; work with children usually needs a DBS check; "
    "work in other people's homes is safer with public liability insurance; food made at home must be registered with the local council; boarding animals at home needs a council licence in England.",
    "UK places and words (reasoning): big cities (London, Manchester, Birmingham, Leeds, Glasgow, Edinburgh) have more customers and more competition; "
    "student towns have many renters and busy people; smaller towns have less competition and word of mouth works faster. Say 'flat', 'halls', 'council', 'car boot sale', 'charity shop'.",
]

# Everyone works on the same idea (1-based position in the list above). Set ASSIGNED_IDEA in Render to change it.
DEFAULT_ASSIGNED_IDEA = 3

# The slide: a Lean Canvas (Ash Maurya) for a side business next to studies or a job. The boxes unlock one by one,
# in the order recommended for the Lean Canvas: problem first, unfair advantage last.
EXAMPLE_BUSINESS = "a mobile bike-repair business"
BLOCKS = [
    {"key": "problem", "title": "The problem", "lean": "Lean Canvas: Problem", "hybrid": False,
     "question": "What annoys or worries your customers most? How do they cope today?",
     "tips": ["Describe the problem in your customer's own words.", "What do they do instead right now, and what does that cost them?",
              "Would they pay to fix it, or only complain about it?"],
     "example": "Bikes break at the worst moment. Shops open when people work, and repairs take days."},
    {"key": "customers", "title": "Who pays", "lean": "Lean Canvas: Customer segments", "hybrid": False,
     "question": "Who has this problem, and who would pay you first?",
     "tips": ["Pick one narrow group, not everyone.", "Where could you find ten of them this week?",
              "Who feels the problem most strongly?"],
     "example": "Students in my halls who cycle to lectures and can't leave a bike at a shop for days."},
    {"key": "uvp", "title": "Why choose you", "lean": "Lean Canvas: Unique value proposition", "hybrid": False,
     "question": "In one sentence: why would someone pick you instead of the alternative?",
     "tips": ["Say what they get, not what you do.", "Would it still beat a shop or a friend who can help?",
              "Make it specific enough that a stranger could repeat it."],
     "example": "Your bike fixed at your door in 30 minutes, for a price you know in advance."},
    {"key": "solution", "title": "What you do", "lean": "Lean Canvas: Solution", "hybrid": False,
     "question": "What will you actually do to fix their problem?",
     "tips": ["List the 1 to 3 things you would really do.", "Keep it to what you can deliver alone in your spare hours.",
              "Which part could you test this week?"],
     "example": "I bring a tool kit, fix punctures, brakes and gears, and send a price by text first."},
    {"key": "channels", "title": "How they find you", "lean": "Lean Canvas: Channels", "hybrid": False,
     "question": "Where will your first customers hear about you, and how do they book?",
     "tips": ["Name the exact place: a group, a platform, a street.", "Which channel is free and quick?",
              "How do they book and pay?"],
     "example": "Two student group chats and flyers in halls. They book by text and pay by transfer."},
    {"key": "income", "title": "Money in", "lean": "Lean Canvas: Revenue streams", "hybrid": False,
     "question": "What will you charge, and how often will a customer pay?",
     "tips": ["Price per job, hour or item?", "How many customers a month make it worth your time?",
              "Will anyone come back and pay again?"],
     "example": "A flat fee per job plus parts at cost. Eight jobs a month would be worth my evenings."},
    {"key": "costs", "title": "Money out", "lean": "Lean Canvas: Cost structure", "hybrid": False,
     "question": "What does it cost to start and to keep going?",
     "tips": ["What must you buy before the first customer?", "Which costs come back every month (fees, travel, supplies)?",
              "What is the cheapest way to start?"],
     "example": "Tools and spare parts to start, then travel and parts top-ups each month."},
    {"key": "metrics", "title": "Numbers to watch", "lean": "Lean Canvas: Key metrics", "hybrid": False,
     "question": "Which 2 or 3 numbers will show that it is working?",
     "tips": ["Pick 2 or 3 numbers you can count every week.", "Include one about money and one about customers.",
              "What number would make you change plan or stop?"],
     "example": "Jobs per week, profit per job, and how many customers book a second time."},
    {"key": "edge", "title": "Your edge", "lean": "Lean Canvas: Unfair advantage", "hybrid": False,
     "question": "What do you have that others can't easily copy or buy?",
     "tips": ["Think of contacts, skills, location, access or reputation.", "Hard work and low prices are easy to copy.",
              "What do your shifts or studies give you that others lack?"],
     "example": "I live in the halls where my customers are, and I already repair friends' bikes."},
]
BLOCK_KEYS = [b["key"] for b in BLOCKS]
ICONS = {}   # no icons or emojis anywhere in the interface
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
    "intro_task": ("You chose {name}. Now design your own business around it on a lean canvas. That is simply a one-page "
                   "business plan with nine short boxes: what problem you solve, who pays, why they pick you, what you "
                   "do, how they find you, money in, money out, the numbers to watch and your edge. Each box you "
                   "complete unlocks the next, and at the end you have a one-slide plan with your own business name, "
                   "pitch and colour."),
    "intro_ai": ("An AI co-founder works with you the whole way. Each time you open a box it shares suggestions and "
                 "asks you questions, and you can reply, ask for ideas or ask for feedback. You decide what goes on "
                 "the slide."),
    "intro_noai": ("You will build the slide on your own. Each box comes with guiding questions, tips and an example "
                   "to help you brainstorm."),
    "intro_time": "You have {minutes} minutes. Your slide is saved automatically while you work.",
    "start": "Start building",
    "canvas_title": "Lean canvas",
    "your_idea": "Your idea",
    "banner_ai": "Your AI co-founder is ready. Open a box: it will challenge your thinking and suggest ideas. Reply, then make them yours.",
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
    "ai_opening": ("Hi, I'm your AI co-founder. In every box I'll challenge your thinking and give you ideas to react to. "
                   "Reply any time, and disagree with me if you like. Start with the first box."),
    "ai_placeholder": "Reply to your co-founder…",
    "ai_thinking": "Thinking of suggestions for \"{box}\"…",
    "ai_for_box": "Suggestions for \"{box}\"",
    "ai_use": "Add to my box",
    "ai_used": "Added",
    "ai_quick_more": "More suggestions",
    "ai_quick_feedback": "Give me feedback",
    "ai_quick_start": "Give me first ideas",
    "ai_quick_setup": "Help me set up my business",
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


# "Money machine" mode (UI_MODE=machine): one screen where the business is a machine that switches on part by part.
# These texts replace the matching TEXT entries and add new ones. The data model (nine boxes) is unchanged.
MACHINE_TEXT = {
    "intro_title": "Build your own money machine",
    "intro_lead": ("Imagine a small business that keeps running while you get on with your life: customers find it, order, "
                   "pay and get served with as little of your time as possible. Below are five side businesses that "
                   "people in the UK can start next to studying or a main job. To begin, choose the one you would like "
                   "to turn into your own machine."),
    "intro_task": ("You chose {name}. Now design your machine. It has nine parts: the problem it solves, who pays, why "
                   "they choose you, what it does, how customers find it, money in, money out, the numbers to watch "
                   "and your edge. Work on the parts in any order. Each part you finish switches that part of the "
                   "machine on. When you are ready, you start the machine and see a ready-made prototype of your business."),
    "intro_ai": ("Compi, an AI co-founder, works next to your machine. Tap any part and Compi gives you a short, concrete tip, "
                 "and you can ask for another idea or tell Compi what you think. You decide what goes into your machine."),
    "intro_noai": ("You will build the machine on your own. Each part comes with guiding questions, tips and an example "
                   "to help you brainstorm."),
    "canvas_title": "Your money machine",
    "banner_ai": "Compi, your AI co-founder, is ready. Tap any part of the machine for a quick tip.",
    "banner_noai": "Tap any part of the machine to switch it on. You can work on the parts in any order.",
    "ai_opening": "Hi, I'm Compi, your AI co-founder. Your idea: {idea}. Tap any part of the machine and we'll build it together, one quick move at a time.",
    "ai_title": "Compi",
    "ai_role": "AI co-founder",
    "ai_quick_more": "Another idea",
    "ai_quick_feedback": "What is weak here?",
    "ai_quick_start": "Give me first ideas",
    "ai_use": "Tap to answer",
    "ai_used": "Sent",
    "ai_placeholder": "Ask Compi…",
    "tab_machine": "Machine",
    "unlocked": "Part online: {name}",
    "m_power": "Machine power",
    "m_parts": "{n} of {total} parts online",
    "m_coins": "Demo coins",
    "m_demo": "Demo animation: the coins are not money and not a forecast of what you could earn.",
    "m_offline": "Offline",
    "m_online": "Online",
    "m_tap": "Tap a part of the machine to switch it on.",
    "m_start": "Start the machine",
    "m_need": "Switch on at least {n} parts before you start the machine.",
    "m_boot1": "Checking your parts…",
    "m_boot2": "Connecting customers, orders and payments…",
    "m_boot3": "Your machine is running.",
    "m_proto_title": "Your prototype is ready",
    "m_proto_lead": "Built only from your own words. This is what your business could look like.",
    "m_proto_tag": "Prototype",
    "m_offer": "Imagine this finished prototype could be yours to keep, free of charge. Two quick questions.",
    "m_scale_q": "How much would you like to turn this prototype into a real business of your own?",
    "m_scale_lo": "Not at all",
    "m_scale_hi": "Very much",
    "m_take_q": "Would you take the prototype if you could?",
    "m_take_yes": "Yes, I would take it",
    "m_take_no": "No, I would leave it",
    "m_finish": "Submit and continue",
    "m_keep": "Keep building",
    "m_close": "Done",
    "m_empty_proto": "Not written yet",
    "m_notes": "Behind the scenes (not on the website)",
}


# "Pitch challenge" mode (UI_MODE=pitch): same nine boxes and one-page canvas, framed as a challenge to build a great pitch
# for a side hustle that could make a profit in the participant's area. Shorter texts, plus short animated mini-videos.
PITCH_TEXT = {
    "intro_title": "The Side Hustle Pitch Challenge",
    "intro_lead": ("Your challenge: build a great pitch for a side hustle that could make a profit where you live. "
                   "Pick one idea to start."),
    "intro_task": ("You chose {name}. Fill in nine short boxes, each takes about two minutes. At the end you have a "
                   "one-page pitch with your own name, tagline and colour."),
    "intro_ai": "Compi, an AI co-founder, gives you a quick, concrete tip for every box. You decide what goes in the pitch.",
    "intro_noai": "Every box comes with a few questions, tips and an example. You decide what goes in the pitch.",
    "start": "Start the challenge",
    "canvas_title": "Your pitch",
    "banner_ai": "Challenge on: build a pitch for a side hustle that could profit in your area. Compi, your AI co-founder, is ready.",
    "banner_noai": "Challenge on: build a pitch for a side hustle that could profit in your area. Fill in the boxes one by one.",
    "name_label": "Business name", "tagline_label": "One-line pitch", "colour_label": "Pitch colour",
    "preview": "Preview pitch", "preview_title": "Your pitch",
    "submit": "Hand in my pitch",
    "need_more": "Please fill in at least {n} boxes before you hand in your pitch.",
    "confirm_title": "Hand in your pitch?", "confirm_text": "You cannot change it afterwards.",
    "timeup": "Time is up. Your pitch has been handed in.",
    "done_text": "Your pitch has been saved. You are being taken to the short survey now.",
    "done_last": "Done, preview my pitch",
    "all_done": "All nine boxes done. Preview your pitch, then hand it in.",
    "tab_slide": "Pitch",
    "ai_opening": "Hi, I'm Compi, your AI co-founder. Your idea: {idea}. Open any box and we'll build it together, one quick move at a time.",
    "ai_title": "Compi", "ai_role": "AI co-founder", "ai_quick_more": "Another idea", "ai_quick_feedback": "What is weak here?", "ai_quick_start": "Give me first ideas",
    "ai_placeholder": "Ask Compi…", "tab_ai": "Compi", "ai_new": "Compi has a new tip",
    "intro_time": ("You have {minutes} minutes. Your pitch is saved automatically while you work. When you hand it in, or when "
                   "time is up, you are taken to the short survey automatically. Please don't use the back button."),
    "v_intro": "Watch the 20-second brief",
    "v_watch": "Watch the 20-second tip",
    "v_replay": "Watch again", "v_close": "Close", "v_skip": "Skip", "v_next": "Next", "v_pause": "Pause", "v_play": "Play",
    "v_end": "Now it's your turn.",
}

# "Shop on the map" mode (UI_MODE=shop): the machine screen, re-skinned as a business on a map of the participant's area and
# framed as the pitch challenge. Layered on top of MACHINE_TEXT and PITCH_TEXT.
SHOP_TEXT = {
    "intro_task": ("You chose {name}. Your business sits on a map of your area. It has nine places to fill in, about two minutes "
                   "each, in any order: the problem, who pays, why they choose you, what you do, how they find you, money in, "
                   "money out, the numbers to watch and your edge. Each place you finish opens on the map. When you are ready, "
                   "submit your project plan."),
    "intro_noai": "Each place comes with a few questions, tips and an example. You decide what goes in the pitch.",
    "banner_ai": "Challenge on: build a pitch for a side hustle that could profit in your area. Tap any place on the map. Compi, your AI co-founder, is ready.",
    "banner_noai": "Challenge on: build a pitch for a side hustle that could profit in your area. Tap any place on the map to work on it.",
    "tab_machine": "Map",
    "unlocked": "Place open: {name}",
    "m_parts": "{n} of {total} places open",
    "m_coins": "Demo visitors",
    "m_demo": "Demo animation: the visitors are not real customers and not a forecast of what you could earn.",
    "m_offline": "Closed", "m_online": "Open",
    "m_tap": "Tap a place on the map to work on it.",
    "m_start": "Submit project plan",
    "m_need": "Open at least {n} places before you submit your project plan.",
    "m_boot1": "Checking your plan…",
    "m_boot2": "Putting your project plan together…",
    "m_boot3": "Your project plan is ready.",
    "m_proto_title": "Your project plan",
    "m_proto_lead": "Download your plan to keep it. Press Keep working to continue brainstorming in a new tab, with no time limit, while you finish the survey here.",
    "m_proto_tag": "Prototype",
    "m_notes": "Notes",
    "m_offer": "Imagine this pitch page could be yours to keep, free of charge. Two quick questions.",
    "m_scale_q": "How much would you like to turn this pitch into a real business of your own?",
    "m_take_q": "Would you take the pitch page if you could?",
    "m_take_yes": "Yes, I would take it", "m_take_no": "No, I would leave it",
    "m_keep": "Keep working",
    "m_download": "Download project plan",
    "m_submit_note": "Press Submit and continue to go to the short survey. Or press Keep working: your plan is submitted, a new tab opens where you can keep brainstorming with no time limit, and this tab continues to the survey."
}


# Mini-videos were removed (they added no value and were too long).
VIDEOS = {}


def texts(mode):
    """The text table for the chosen interface mode: True or "machine", "pitch", "shop", otherwise the default canvas."""
    if mode is True or mode == "machine":
        return {**TEXT, **MACHINE_TEXT}
    if mode == "pitch":
        return {**TEXT, **PITCH_TEXT}
    if mode == "shop":
        return {**TEXT, **MACHINE_TEXT, **PITCH_TEXT, **SHOP_TEXT}
    return TEXT
