# Planetarium API Service

Planetarium API Service is a Django RESTful API backend for managing a planetarium's resources, including shows, show sessions, reservations, and more. It provides endpoints for creating, updating and retrieving data related to various aspects of a planetarium's operations.

## Features

- **Shows**: Manage information about astronomy shows, including title, description, and themes.
- **Domes**: Keep track of planetarium domes, including name, number of rows, and seats in each row.
- **Sessions**: Schedule show sessions within planetarium domes, specifying the astronomy show, date, and available seats.
- **Reservations**: Allow users to make reservations for show sessions, selecting seats within the dome.
- **User system**: Allow to create user profiles, update user info and separate user by rights

## Technologies Used

- **Django**: Python web framework used for backend development.
- **Django REST Framework (DRF)**: Toolkit for building Web APIs with Django.
- **SQLite**: Lightweight SQL database used for development.
- **PostgreSQL**: Production-ready relational database used for deployment.
- **Docker**: Containerization platform used for packaging the application and its dependencies.
- **Docker Compose**: Tool for defining and running multi-container Docker applications.
- **pytest**: Testing framework used for writing and executing tests.

## API Reference

### User API resources
Note: **All of resources is Required to be authenticated. In this case you should authenticate before using service**

```http
POST /api/user/register/
```
| Key | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `email`      | `email-string` | Your email | **Required**. |
| `password`  | `string` | Password | **Required**. |

After that, you should to get your auth-token with provided user-data

```http
POST /api/user/login/
```

Also, you can update your email or password using next resources with your Token like a header:

```http
PUT|PATH /api/user/me/
```

| Key | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `email/password`      | `email/string` | Add new data in body with related key | 

example body:
**{
    "email": "newemail@example.com
}**

# RESOURCES

#### Get list of information resources

```http
  GET api/planetarium/
```

**Note: You can get further resources if you are authenticated**

## Get list of show themes

```http
  GET /api/planetarium/show_themes/
```

To get concrete theme use params **name**:
```http
  GET /api/planetarium/show_themes/?name=Example
```
It returns you distinct value wich contains provided params


#### Create new theme (possible if user has admin permissions)

```http
  POST /api/planetarium/show_themes/
```

| Key | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `name`      | `string` | Name of theme | **Required**. |

## Get list of Astronomy Show

```http
  GET /api/planetarium/shows/
```

To get concrete Show you can provide 2 params:

| Param | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `theme`  | `string` | Name of theme |
| `title`  | `string` | Show title |

It returns you distinct value wich contains provided params

or Get it by id

```http
  GET /api/planetarium/shows/{id: int}/
``` 

#### Create Astronomy Show (possible if user has admin permissions)

```http
  POST /api/planetarium/shows/
```

| Key | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `title`  | `string` | Show title | **requried** |
| `description`  | `string` | Description of the show | **requried** |
| `theme`  | `list of int` | id (primary key) existing Themes | **requried** |


## Get list of planetarium dome

```http
  GET /api/planetarium/domes/
```

To get concrete Dome you can provide "name" param

```http
  GET /api/planetarium/domes/?name=Example
```

#### Create Dome (possible if user has admin permissions)

```http
  POST /api/planetarium/domes/
```

| Key | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `name`  | `string` | Dome name | **requried** |
| `rows`  | `int` | Count of rows | **requried** |
| `seats_in_row`  | `int` | Count of seats | **requried** |

## Get list of Show Sessions

```http
  GET /api/planetarium/sessions/
```

or Get it by id

```http
  GET /api/planetarium/sessions/{id: int}/
``` 

#### Create Show sessions (possible if user has admin permissions)

```http
  POST /api/planetarium/sessions/
```

| Key | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `astronomy_show`  | `int` | id (pk) from Astronomy Show | **requried** |
| `planetarium_dome`  | `int` | id (pk) from Planetarium Dome | **requried** |
| `show_time`  | `string (datetime format ISO 8601 ` | Example: "2024-03-28T12:00:00" | **requried** |

## Get Reservation list

```http
  GET /api/planetarium/reservations/
```

#### Create reservation (possible for all authenticated users)

```http
  POST /api/planetarium/reservations/
```

**NOTE: IT PROVIDE LIST OF DICTIONARY WITH HEAD KEY "*TICKETS*"**

| Key | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `row`  | `int` | Selected row | **requried** |
| `seat`  | `int` | Selected seat | **requried** |
| `show_session`  | `int ` | id (pk) from Show Session | **requried** |

Example body:
{
    "tickets": [
        {
            "row": 1,
            "seat": 7,
            "show_session": 1
        },
        {
            "row": 1,
            "seat": 8,
            "show_session": 1
        }
    ]
}

**Be sure, you cant take seats which not allowed to current session or not in range which contains related Dome**

## Admin-panel

You can enter to admin panel using url

*example*:
http://127.0.0.1:8000/admin/user/user/add/

## Additional information

**User with admin permissions**
- Username (email): test_admin@admin.com
- Password: 84S44TxhYy



## Feedback

If you have any feedback, please reach out to me at sergmarten21@gmail.com

