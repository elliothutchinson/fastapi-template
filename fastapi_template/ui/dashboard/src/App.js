import { useState } from 'react';
import './App.css';

const Register = (props) => {
    const [username, setUsername] = useState("");
    const [fullName, setFullName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const register = (e) => {
        props.setRegister(false);
    };
    return (
        <div>
            <h1>Register</h1>
            <form>
                <label>Username</label>
                <input value={username} onChange={e => setUsername(e.target.value)}></input>
                <label>Full Name</label>
                <input value={fullName} onChange={e => setFullName(e.target.value)}></input>
                <label>Email</label>
                <input value={email} onChange={e => setEmail(e.target.value)}></input>
                <label>Password</label>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)}></input>
                <button onClick={register}>Register</button>
            </form>
            <button onClick={register}>Login</button>
        </div>
    );
};

const Login = (props) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [register, setRegister] = useState(false);
    
    const login = (e) => {
        props.setLogState({
            "loggedIn": true,
            "token": "asdf",
            "username": username
        });
    };

    const registerHandle = (e) => {
        setRegister(true);
    }

    if (register) {
        return (
            <Register setRegister={setRegister}></Register>
        )
    }

    return (
        <div>
            <h1>Login</h1>
            <form>
                <label>Username</label>
                <input value={username} onChange={e => setUsername(e.target.value)}></input>
                <label>Password</label>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)}></input>
                <button onClick={login}>Login</button>
            </form>
            <button onClick={registerHandle}>Sign Up</button>
        </div>
    );
};

const Header = (props) => {
    const logout = (e) => {
        props.setLogState({
            "loggedIn": false,
            "token": "",
            "username": "",
        })
    };
    return (
        <div>
            <p>Welcome, {props.logState.username}</p>
            <button onClick={logout}>Logout</button>
        </div>

    );
};

const Todos = (props) => {
    const [todos, setTodos] = useState(
        [{
            "todo_id": "asdf",
            "todo_list": "shopping",
            "description": "get steak!",
            "completed": false,
            "date_created": "2021-11-03T16:26:40.872Z",
            "date_modified": null
        },
        {
            "todo_id": "asdf",
            "todo_list": "shopping",
            "description": "get salmon",
            "completed": false,
            "date_created": "2021-11-03T16:26:40.872Z",
            "date_modified": null
        }
    ]
    );
    return (
        <div>
            <h1>Todos</h1>
            <ul>
                {
                    todos.map((t) => {
                    return (<li><Todo todo={t}></Todo></li>)
                })}
            </ul>
        </div>
    );
};

const Todo = (props) => {
    // const [todo, setTodo] = useState([]);
    return (
        <div>
            <input value={props.todo.description}></input>
            <input type="checkbox"></input>
        </div>
    );
};


const App = () => {
    const [logState, setLogState] = useState({
        "loggedIn": false,
        "token": "",
        "username": "",
    });

    if (!logState.loggedIn) {
        return (
            <div className="App">
                <Login setLogState={setLogState}></Login>
            </div>
        );
    }
    return (
        <div className="App">
            <Header logState={logState} setLogState={setLogState}></Header>
            <Todos></Todos>
        </div>
    );
};

export default App;
