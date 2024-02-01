import { API_V1_URL } from '../common/contants';
import { deleteApi, getApi, postApi, putApi } from '../common/utils';


export async function fetchTodoLists(authToken) {
  const url = `${API_V1_URL}/todo/list/`;
  let result = {};
  try {
    result = await getApi(url, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred fetching todo lists.'];
  }
  return result;
}


export async function createTodoList(todoListCreate, authToken) {
  const url = `${API_V1_URL}/todo/list/`;
  let result = {};
  try {
    result = await postApi(url, todoListCreate, true, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred creating todo list.'];
  }
  return result;
}


export async function updateTodoList(todoListId, todoListUpdate, authToken) {
  const url = `${API_V1_URL}/todo/list/${todoListId}`;
  let result = {};
  try {
    result = await putApi(url, todoListUpdate, true, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred updating todo list.'];
  }
  return result;
}


export async function deleteTodoList(todoListId, authToken) {
  const url = `${API_V1_URL}/todo/list/${todoListId}`;
  let result = {};
  try {
    result = await deleteApi(url, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred deleting todo list.'];
  }
  return result;
}


export async function fetchAllTodos(incompleteOnly, authToken) {
  const url = `${API_V1_URL}/todo/task/?incomplete_only=${incompleteOnly}`;
  let result = {};
  try {
    result = await getApi(url, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred fetching todos.'];
  }
  return result;
}


export async function fetchTodos(todoListId, authToken) {
  const url = `${API_V1_URL}/todo/task/?todo_list_id=${todoListId}`;
  let result = {};
  try {
    result = await getApi(url, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred fetching todos.'];
  }
  return result;
}


export async function createTodo(todoCreate, authToken) {
  const url = `${API_V1_URL}/todo/task/`;
  let result = {};
  try {
    result = await postApi(url, todoCreate, true, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred creating todo.'];
  }
  return result;
}


export async function updateTodo(todoId, todoUpdate, authToken) {
  const url = `${API_V1_URL}/todo/task/${todoId}`;
  let result = {};
  try {
    result = await putApi(url, todoUpdate, true, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred updating todo.'];
  }
  return result;
}


export async function deleteTodo(todoId, authToken) {
  const url = `${API_V1_URL}/todo/task/${todoId}`;
  let result = {};
  try {
    result = await deleteApi(url, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred deleting todo.'];
  }
  return result;
}
