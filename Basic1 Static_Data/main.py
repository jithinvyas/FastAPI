from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title:str
    content:str
    published: bool = True
    rating: Optional[int] = None

my_posts = [
            {'id':1 ,'title':'This is First title', 'content': 'The content for FastAPI', 'published': False, 'rating': 4},
            {'id':2 ,'title':'This is Second title', 'content': 'The content for Second Title', 'published':True, 'rating': 5},
            {'id':3 ,'title':'This is Third title', 'content': 'This is Hard-coded', 'published': True, 'rating': 2}
 ]   

@app.get('/')
def home():
    return {'msg': 'Hello World'}

@app.get('/posts')
def get_posts():
    return {'data': my_posts}

@app.post('/createPosts', status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    mydic = post.model_dump()
    mydic['id'] = randrange(0,1000000)
    my_posts.append(mydic)
    return {"data": mydic}


@app.get('/posts/latest')  # since execution happens from top to bottom
def latest_post():
    latest = my_posts[len(my_posts)-1]
    return {'data': latest}

def findID(id):
    for d in my_posts:
        if d['id']==id:
            return d

@app.get('/posts/{id}')  # note:- {id} is int convtd
def get_posts(id:int):
    data = findID(id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with ID: {id} was not found")
    return {"data": data}

def findIndex_2delete(id):
    for i,d in enumerate(my_posts):
        if d['id'] == id:
            return i

@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def deletePost(id:int):
    index = findIndex_2delete(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with {id} doesn't exist")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def updatePost(id:int, post: Post):
    index = findIndex_2delete(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with {id} doesn't exist")
    
    post_dict = post.model_dump() # dict
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {'data': post_dict}