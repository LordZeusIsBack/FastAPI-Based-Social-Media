from fastapi import FastAPI, HTTPException
from src.schemas import PostCreate


app = FastAPI()


text_posts = {
    1: {'title': 'New Beginnings', 'content': 'Here comes the money!'},
    2: {'title': 'Rise and Grind', 'content': 'Early bird gets the code.'},
    3: {'title': 'Debugging Blues', 'content': 'Why is it always a semicolon?'},
    4: {'title': 'Coffee Overload', 'content': 'Caffeine: the real programming language.'},
    5: {'title': 'AI Musings', 'content': 'Will machines ever dream of electric sheep?'},
    6: {'title': 'Late Night Coding', 'content': 'When the world sleeps, I compile.'},
    7: {'title': 'Weekend Vibes', 'content': 'A well-deserved break from the matrix.'},
    8: {'title': 'Data Dreams', 'content': 'Rows, columns, and a little bit of magic.'},
    9: {'title': 'MUN Flashback', 'content': 'Debate, diplomacy, and a dash of drama.'},
    10: {'title': 'Hindustani Harmony', 'content': 'Raag Yaman meets neural networks.'},
    11: {'title': 'Tech Nostalgia', 'content': 'Remember when floppy disks were a thing?'},
    12: {'title': 'The Vegetarian Code', 'content': '100% plant-based, bug-free logic.'},
    13: {'title': 'Django Diaries', 'content': 'Backends are beautiful, trust me.'},
    14: {'title': 'Model Madness', 'content': 'Training AI feels like raising a toddler.'},
    15: {'title': 'The Calm Before Deploy', 'content': 'May the server be ever in your favor.'},
    16: {'title': 'Statistical Shenanigans', 'content': 'p < 0.05 or bust.'},
    17: {'title': 'AI for All', 'content': 'Democratizing intelligence, one dataset at a time.'},
    18: {'title': 'The Great Merge', 'content': 'Git conflicts: modern-day duels.'},
    19: {'title': 'Cloud Chaser', 'content': 'Deploying dreams on digital skies.'},
    20: {'title': 'Final Commit', 'content': 'Good code never dies; it just gets refactored.'}
}


@app.get('/post')
def get_all_posts():
    return text_posts

@app.get('/post/{post_id}')
def get_post_by_id(post_id: int):
    if post_id not in text_posts:
        raise HTTPException(404, 'Post ID Invalid!')
    return text_posts.get(post_id)

@app.post('/post')
def create_post(post_create: PostCreate):
    new_post = {'title': post_create.title, 'content': post_create.content}
    text_posts[max(text_posts.keys()) + 1] = new_post
    return new_post
