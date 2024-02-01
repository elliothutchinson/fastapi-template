import { useEffect, useState } from 'react';
import { Form, Modal, INPUT, SELECT, CHECKBOX, CheckboxField } from "../common/Components";
import { 
  fetchTodoLists,
  createTodoList,
  updateTodoList,
  deleteTodoList,
  fetchAllTodos,
  createTodo,
  updateTodo,
  deleteTodo,
} from './api';
import { ERROR } from '../header/Alert';


const ALL_TODOS = 'ALL';


function AddTodoList(props) {
  const [listName, setListName] = useState('');
  const [modalState, setModalState] = useState(false);

  const modalId = 'addTodoListModalId';

  function toggleModal() {
    if (!modalState) {
      setModalState(true);
      document.getElementById(modalId).showModal();
    } else {
      setModalState(false);
      setListName('');
      document.getElementById(modalId).close();
    }
  }

  async function handleCreate(e) {
    e.preventDefault();
    const todoListId = crypto.randomUUID();
    const spinner = props.spinnerControl.create();
    const result = await createTodoList({
      todoListId,
      listName,
    }, props.authToken);
    props.spinnerControl.remove(spinner);
    console.log('create todo result: ', result);

    if (result.errors) {
      for (const error of result.errors) {
        props.alertControl.add({type: ERROR, message: error});
      }
    } else {
      toggleModal();
      props.dataRefresh();
    }
  }

  const fields = [
    {
      name: 'List Name',
      required: true,
      type: INPUT,
      value: listName,
      handleChange: setListName,
    },
  ];

  const cta = {
    name: 'Save',
    handleClick: handleCreate,
  };

  const form = <Form key="addTodoListForm" formTitle="Create List" fields={fields} cta={cta} />;

  return (
    <>
      <button className="btn btn-primary" onClick={toggleModal}>+ List</button>
      <Modal modalId={modalId} children={[form]} modalState={modalState} toggleModal={toggleModal} />
    </>
  );
}


function EditTodoList(props) {
  const [listName, setListName] = useState(props.activeTodoList.todoList.listName);
  const [modalState, setModalState] = useState(false);

  const modalId = 'editTodoListModalId';

  function toggleModal() {
    if (!modalState) {
      setModalState(true);
      document.getElementById(modalId).showModal();
    } else {
      setModalState(false);
      setListName('');
      props.dismissEdit();
      document.getElementById(modalId).close();
    }
  }

  useEffect(() => {
    if (props.editList) {
      toggleModal();
    }
    const updatedListName = props.activeTodoList.todoList.listName || '';
    setListName(updatedListName);
  }, [props.activeTodoList, props.editList]);

  async function handleUpdate(e) {
    e.preventDefault();
    const todoListId = props.activeTodoList.todoList.todoListId;
    const spinner = props.spinnerControl.create();
    const result = await updateTodoList(todoListId, {
      listName,
    }, props.authToken);
    props.spinnerControl.remove(spinner);
    console.log('update todo list result: ', result);

    if (result.errors) {
      for (const error of result.errors) {
        props.alertControl.add({type: ERROR, message: error});
      }
    } else {
      toggleModal();
      props.dataRefresh();
    }
  }

  async function handleDelete(e) {
    e.preventDefault();
    const todoListId = props.activeTodoList.todoList.todoListId;
    const spinner = props.spinnerControl.create();
    const result = await deleteTodoList(todoListId, props.authToken);
    props.spinnerControl.remove(spinner);
    console.log('delete todo result: ', result);

    if (result.errors) {
      for (const error of result.errors) {
        props.alertControl.add({type: ERROR, message: error});
      }
    } else {
      toggleModal();
      props.dataRefresh();
    }
  }

  const fields = [
    {
      name: 'List Name',
      required: true,
      type: INPUT,
      value: listName,
      handleChange: setListName,
    },
  ];

  const child = (
    <div key="delete-todo-list" className="space-x-2">
      <a className="link" onClick={handleDelete}>Delete</a>
    </div>
  );

  const cta = {
    name: 'Save',
    handleClick: handleUpdate,
  };

  const form = <Form key="editTodoListForm" formTitle="Edit List" fields={fields} children={[child]} cta={cta} />;

  return (
    <>
      <Modal modalId={modalId} children={[form]} modalState={modalState} toggleModal={toggleModal} />
    </>
  );

}


function AddTodo(props) {
  const [listName, setListName] = useState(props.activeTodoList.todoList.todoListId);
  const [description, setDescription] = useState('');
  const [completed, setCompleted] = useState(false);
  const [modalState, setModalState] = useState(false);

  const modalId = 'addTodoModalId';

  useEffect(() => {
    let updatedListName = props.activeTodoList.todoList.todoListId;
    if (updatedListName === ALL_TODOS) {
      updatedListName = props.todoLists ? props.todoLists[0].todoListId : '';
    }
    setListName(updatedListName);
  }, [props.activeTodoList]);

  function toggleModal() {
    if (!modalState) {
      setModalState(true);
      document.getElementById(modalId).showModal();
    } else {
      setModalState(false);
      setListName(props.activeTodoList.todoList.todoListId);
      setDescription('');
      setCompleted(false);
      document.getElementById(modalId).close();
    }
  }

  async function handleCreate(e) {
    e.preventDefault();
    const todoId = crypto.randomUUID();
    const spinner = props.spinnerControl.create();
    const result = await createTodo({
      todoId,
      todoListId: listName,
      description,
      completed,
    }, props.authToken);
    props.spinnerControl.remove(spinner);
    console.log('create todo result: ', result);

    if (result.errors) {
      for (const error of result.errors) {
        props.alertControl.add({type: ERROR, message: error});
      }
    } else {
      toggleModal();
      props.dataRefresh();
    }
  }

  const options = props.todoLists.map(t => ({value: t.todoListId, name: t.listName}));

  const fields = [
    {
      name: 'List Name',
      required: true,
      type: SELECT,
      value: listName,
      options,
      handleChange: setListName,
    },
    {
      name: 'Description',
      required: true,
      type: INPUT,
      value: description,
      handleChange: setDescription,
    },
    {
      name: 'Completed',
      required: false,
      type: CHECKBOX,
      value: completed,
      handleChange: setCompleted,
    },
  ];

  const cta = {
    name: 'Save',
    handleClick: handleCreate,
  };

  const form = <Form key="addTodoForm" formTitle="Create Todo" fields={fields} cta={cta} />;

  return (
    <>
      <button className="btn btn-primary" onClick={toggleModal}>+ Todo</button>
      <Modal modalId={modalId} children={[form]} modalState={modalState} toggleModal={toggleModal} />
    </>
  );
}


function EditTodo(props) {
  const [listName, setListName] = useState(props.activeTodoList.todoList.listName);
  const [description, setDescription] = useState('');
  const [completed, setCompleted] = useState(false);
  const [modalState, setModalState] = useState(false);

  const modalId = 'editTodoModalId';

  function toggleModal() {
    if (!modalState) {
      setModalState(true);
      document.getElementById(modalId).showModal();
    } else {
      setModalState(false);
      setListName('');
      setDescription('');
      setCompleted(false);
      props.dismissEdit();
      document.getElementById(modalId).close();
    }
  }

  useEffect(() => {
    if (props.editTodo) {
      toggleModal();
    }
    let updatedListName = props.activeTodoList.todoList.todoListId;
    if (updatedListName === ALL_TODOS) {
      updatedListName = props.todoLists ? props.todoLists[0].todoListId : '';
    }
    setListName(updatedListName);
    setDescription(props.activeTodo.description);
    setCompleted(props.activeTodo.completed);
  }, [props.activeTodo, props.editTodo]);

  async function handleUpdate(e) {
    e.preventDefault();
    const todoId = props.activeTodo.todoId;
    const spinner = props.spinnerControl.create();
    const result = await updateTodo(todoId, {
      todoListId: listName,
      description,
      completed,
    }, props.authToken);
    props.spinnerControl.remove(spinner);
    console.log('update todo result: ', result);

    if (result.errors) {
      for (const error of result.errors) {
        props.alertControl.add({type: ERROR, message: error});
      }
    } else {
      toggleModal();
      props.dataRefresh();
    }
  }

  async function handleDelete(e) {
    e.preventDefault();
    const todoId = props.activeTodo.todoId;
    const spinner = props.spinnerControl.create();
    const result = await deleteTodo(todoId, props.authToken);
    props.spinnerControl.remove(spinner);
    console.log('delete todo result: ', result);

    if (result.errors) {
      for (const error of result.errors) {
        props.alertControl.add({type: ERROR, message: error});
      }
    } else {
      toggleModal();
      props.dataRefresh();
    }
  }

  const options = props.todoLists.map(t => ({value: t.todoListId, name: t.listName}));

  const fields = [
    {
      name: 'List Name',
      required: true,
      type: SELECT,
      value: listName,
      options,
      handleChange: setListName,
    },
    {
      name: 'Description',
      required: true,
      type: INPUT,
      value: description,
      handleChange: setDescription,
    },
    {
      name: 'Completed',
      required: false,
      type: CHECKBOX,
      value: completed,
      handleChange: setCompleted,
    },
  ];

  const child = (
    <div key="delete-todo" className="space-x-2">
      <a className="link" onClick={handleDelete}>Delete</a>
    </div>
  );

  const cta = {
    name: 'Save',
    handleClick: handleUpdate,
  };

  const form = <Form key="editTodoForm" formTitle="Edit Todo" fields={fields} children={[child]} cta={cta} />;

  return (
    <>
      <Modal modalId={modalId} children={[form]} modalState={modalState} toggleModal={toggleModal} />
    </>
  );
}


function TodoLists(props) {
  const [editList, setEditList] = useState(false);

  function handleClick(todoListId) {
    props.setActiveTodoList(todoListId);
    if (todoListId === props.activeTodoList.todoList.todoListId) {
      setEditList(true);
    }
  }

  function dismissEdit() {
      setEditList(false);
  }

  const allLists = !props.todoLists.length ? null :
    <li key={ALL_TODOS}>
      <a
        className={ALL_TODOS == props.activeTodoList.todoList.todoListId ? "active" : null}
        onClick={() => props.setActiveTodoList(ALL_TODOS)}
      >
        [All]
      </a>
    </li>;

  const lists = props.todoLists.map(t => {
    return (
      <li key={t.todoListId}>
        <a 
          className={t.todoListId == props.activeTodoList.todoList.todoListId ? "active cursor-pointer" : null}
          onClick={() => handleClick(t.todoListId)}
        >
          {t.listName}
        </a>
      </li>
    );
  });

  const noLists = props.todoLists.length ? null :
    <li key="No Lists">
      <a>No Lists</a>
    </li>;

  return (
    <div>
      <AddTodoList
        alertControl={props.alertControl}
        spinnerControl={props.spinnerControl}
        authToken={props.authToken}
        dataRefresh={props.dataRefresh}
      />
      <EditTodoList
        alertControl={props.alertControl}
        spinnerControl={props.spinnerControl}
        authToken={props.authToken}
        activeTodoList={props.activeTodoList} 
        editList={editList}
        dismissEdit={dismissEdit}
        dataRefresh={props.dataRefresh}
      />

      <ul className="menu bg-base-200 w-56">
        {allLists}
        {lists}
        {noLists}
      </ul>
    </div>
  );
}


function TodoListDetails(props) {
  const [editTodo, setEditTodo] = useState(false);
  const [activeTodo, setActiveTodo] = useState({});

  function handleClick(todo) {
    setEditTodo(true);
    setActiveTodo(todo);
  }

  function dismissEdit() {
      setEditTodo(false);
  }

  const noTodos = props.activeTodoList.todos.length ? null :
    <tr key="no todos" className="hover">
      <td></td>
      <td>No todos</td>
      <td></td>
    </tr>;

  const todos = props.activeTodoList.todos.map((todo, index) => {
    return (
      <tr key={todo.todoId} className="hover cursor-pointer" onClick={() => handleClick(todo)}>
        <td>{index + 1}</td>
        <td>{todo.description}</td>
        <td><input className="checkbox" type="checkbox" readOnly={true} checked={todo.completed} /></td>
      </tr>
    );
  });

  const addTodoComponent = !props.todoLists.length ? null :
    <AddTodo
      alertControl={props.alertControl}
      spinnerControl={props.spinnerControl}
      todoLists={props.todoLists}
      activeTodoList={props.activeTodoList}
      dataRefresh={props.dataRefresh}
      authToken={props.authToken}
    />;
  const editTodoComponent = !props.todoLists.length ? null :
    <EditTodo
      alertControl={props.alertControl}
      spinnerControl={props.spinnerControl}
      todoLists={props.todoLists}
      activeTodoList={props.activeTodoList}
      activeTodo={activeTodo} 
      editTodo={editTodo}
      dismissEdit={dismissEdit}
      dataRefresh={props.dataRefresh}
      authToken={props.authToken}
    />;

  return (
    <div>
      {addTodoComponent}
      <CheckboxField
        name="Hide completed" 
        value={props.hideCompleted}
        handleChange={props.setHideCompleted}
      />
      {editTodoComponent}
      <table className="table">
        <thead>
          <tr>
            <th></th>
            <th>Description</th>
            <th>Completed</th>
          </tr>
        </thead>
        <tbody>
          {noTodos}
          {todos}
        </tbody>
      </table>
    </div>
  );
}


export default function Todo(props) {
  const [activeTodoList, setActiveTodoList] = useState({
    todoList: {},
    todos: [],
  });
  const [todoLists, setTodoLists] = useState([]);
  const [todos, setTodos] = useState([]);
  const [refreshData, setRefreshData] = useState(Math.random())
  const [hideCompleted, setHideCompleted] = useState(false);

  function dataRefresh() {
    setRefreshData(Math.random());
  }

  useEffect(() => {
    const fetchData = async () => {
      const todoListsSpinner = props.spinnerControl.create();
      const todoListsResults = await fetchTodoLists(props.authToken);
      props.spinnerControl.remove(todoListsSpinner);
      console.log('fetch todo lists result: ', todoListsResults);

      if (todoListsResults.errors) {
        for (const error of todoListsResults.errors) {
          props.alertControl.add({type: ERROR, message: error});
        }
      } else {
        setTodoLists(todoListsResults.data);

        let nextTodoList = {};
        let nextTodos = [];
        
        if (todoListsResults.data.length > 0) {
          nextTodoList = todoListsResults.data[0];
        }

        if (activeTodoList.todoList.todoListId) {
          const prevActiveTodoList = todoListsResults.data
            .filter(t => t.todoListId === activeTodoList.todoList.todoListId)
            .reduce((a, c) => c, null);
          if (prevActiveTodoList) {
            nextTodoList = prevActiveTodoList;
          }
        }

        if (activeTodoList.todoList.todoListId === ALL_TODOS) {
          nextTodoList = activeTodoList.todoList;
        }

        const todosSpinner = props.spinnerControl.create();
        const todosResult = await fetchAllTodos(hideCompleted, props.authToken);
        props.spinnerControl.remove(todosSpinner);
        console.log('fetch todos result: ', todosResult);
        
        if (todosResult.errors) {
          for (const error of todosResult.errors) {
            props.alertControl.add({type: ERROR, message: error});
          }
        } else {
          setTodos(todosResult.data);

          if (nextTodoList.todoListId === ALL_TODOS) {
            nextTodos = todosResult.data;
          } else {
            const filteredTodos = todosResult.data.filter(t => t.todoListId === nextTodoList.todoListId);
            nextTodos = filteredTodos;
          }
        }

        setActiveTodoList({
          todoList: nextTodoList,
          todos: nextTodos,
        });
      }
    };
    fetchData();
  }, [refreshData, hideCompleted]);

  function setActiveTodoListWrapper(todoListId) {
    let nextTodoList = {};
    let nextTodos = [];

    if (todoListId === ALL_TODOS) {
      nextTodoList = {todoListId: ALL_TODOS};
      nextTodos = [...todos];
    } else {
      nextTodoList = todoLists.filter(t => t.todoListId === todoListId).reduce((a, c) => c, null);
      nextTodos = todos.filter(t => t.todoListId === todoListId);
    }

    setActiveTodoList({
      todoList: nextTodoList,
      todos: nextTodos,
    });
  }

  return (
    <>
      <h2 className="text-2xl text-center">Todos</h2>
      <div className="md:flex md:justify-center sm:content-center">
        <TodoLists
          alertControl={props.alertControl}
          spinnerControl={props.spinnerControl}
          todoLists={todoLists}
          activeTodoList={activeTodoList}
          setActiveTodoList={setActiveTodoListWrapper}
          authToken={props.authToken}
          dataRefresh={dataRefresh}
        />
        <div className="overflow-x-auto">
          <TodoListDetails
            alertControl={props.alertControl}
            spinnerControl={props.spinnerControl}
            todoLists={todoLists}
            activeTodoList={activeTodoList}
            authToken={props.authToken}
            dataRefresh={dataRefresh}
            hideCompleted={hideCompleted}
            setHideCompleted={setHideCompleted}
          />
        </div>
      </div>
    </>
  );
}
