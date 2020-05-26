# API_Juanpa

## POST api/login/
```json
Send
{
    "username": "jordan",
    "password": "jordan"
}
Respond
{
    "token": "49f25c5250b1665852ad05b67d11c830cebbcc30"
}
```
## GET api/posts/
```json
Send
{
    http get request
}
Respond
[
    {
        "id": 89,
        "uri": "data:image/png;base64,iVBORw0KGgoAAIAABJRU5ErkJggg==",
        "title": "title98",
        "summary": "juanpo"
    },
    {
        "id": 90,
        "uri": "data:image/png;base64,iVBORw0KGgoAAIAABJRU5ErkJggg==",
        "title": "title73",
        "summary": "juanpa"
    },
    {
        "id": 91,
        "uri": "data:image/png;base64,iVBORw0KGgoAAIAABJRU5ErkJggg==",
        "title": "title73",
        "summary": "juanpa"
    }
]
```
## GET api/posts/?id=49
```json
Send
{
    http get request
}
Respond
[
    {
        "id": 90,
        "uri": "data:image/png;base64,iVBORw0KGgoAAIAABJRU5ErkJggg==",
        "title": "title73",
        "summary": "juanpa"
    },
    {
        "id": 74,
        "text": "Titl678",
        "font_size": 12,
        "post": 90
    },
    {
        "id": 71,
        "text": "paraaa678",
        "font_size": 12,
        "color": "#ffff",
        "font_weight": 10,
        "post": 90
    },
    {
        "id": 22,
        "uri": "data:image/png;base64,iVBORw0KGgoAAIAABJRU5ErkJggg==",
        "weight": 23,
        "height": 12,
        "post": 90
    },
    {
        "id": 22,
        "string": "The code 678",
        "language": "node",
        "post": 90
    },
    {
        "id": 17,
        "uri": "data:video/mp4;base64,AAAAGGZ0eXBtcDQyA1wWWAAAADDEwL",
        "weight": 12,
        "height": 13,
        "post": 90
    }
]
```
## POST api/posts/
```json
Send
{
    "token": "49f25c5250b1665852ad05b67d11c830cebbcc30",
    "post": [
        {
            "title": "title44",
            "uri": "iVBORw0KGgoAAAANSUhEUgA...",
            "summary": "string"
        },
        {
            "type": "title",
            "text": "Titl678",
            "font_size": 12
        },
        {
            "type": "paragraph",
            "text": "paraaa678",
            "font_size": 12,
            "color": "#ffff",
            "font_weight": 10
        },
        {
            "type": "image",
            "uri": "iVBORw0KGgoAAAANSUhEUg...",
            "weight": 23,
            "height": 12
        },
        {
            "type": "code",
            "string": "The code 678",
            "language": "node"
        },
        {
            "type": "video",
            "uri": "iVBORw0KGgoAAAANSUh...",
            "weight": 120,
            "height": 130
        }
    ]
}
Respond
{
    "respond": "success"
}
```
## PUT api/posts/?id=49
```json
Send
{
    "token": "49f25c5250b1665852ad05b67d11c830cebbcc30",
    "post": [
        {
            "title": "title44",
            "uri": "iVBORw0KGgoAAAANSUhEUgA...",
            "summary": "string"
        },
        {
            "type": "title",
            "text": "Titl678",
            "font_size": 12
        },
        {
            "type": "paragraph",
            "text": "paraaa678",
            "font_size": 12,
            "color": "#ffff",
            "font_weight": 10
        },
        {
            "type": "image",
            "uri": "iVBORw0KGgoAAAANSUhEUg...",
            "weight": 23,
            "height": 12
        },
        {
            "type": "code",
            "string": "The code 678",
            "language": "node"
        },
        {
            "type": "video",
            "uri": "iVBORw0KGgoAAAANSUh...",
            "weight": 120,
            "height": 130
        }
    ]
}
Respond
{
    "respond": "success"
}
```
## DELETE api/posts/?id=49
```json
Send
{
    "token": "49f25c5250b1665852ad05b67d11c830cebbcc30"
}
Respond
{
    "respond": "success"
}
```
