from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2  # https://www.psycopg.org/docs/usage.html
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title:str
    content:str
    published: bool = True

while True:  # if while loop not used, then our code works without database connection being successful
    try:
        conn = psycopg2.connect(host='localhost',
                                database='jv-fastapi',
                                user='postgres',
                                password='123456',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database Connection was Successful")
        break

    except Exception as error:
        print("Connecting to the database failed")
        print("Error: ", error)
        time.sleep(3)
   

@app.get('/')
def home():
    return {'msg': 'Hello World'}

@app.get('/posts')
def get_posts():
    cursor.execute("""SELECT * FROM posts """)
    posts = cursor.fetchall()
    print(posts)
    return {'data': posts}

@app.post('/createPosts', status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts(title, content, published) 
                   values (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()

    conn.commit()
    return {"data": new_post}


@app.get('/posts/latest')  # ('/latest' is a string better keep it on top, As below function is about accessing ID as integer)
def latest_post(latest:int = {id}):
    cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC """)
    latest = cursor.fetchone()
    return {'data': latest}


@app.get('/posts/{id}')  # note:- {id} is int convtd
def get_posts(id:int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id), )) # make sure to have a comma at end to avoid potential issues
    data = cursor.fetchone()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with ID: {id} was not found")
    return {"data": data}


@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def deletePost(id:int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id), ))
    deleted_post = cursor.fetchone()
    conn.commit()
    
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with {id} doesn't exist")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def updatePost(id:int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s,
                                        content = %s,
                                        published = %s 
                                    WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id), ))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with {id} doesn't exist")
    
    return {'data': updated_post}