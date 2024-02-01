import { test, expect, beforeAll, afterAll, afterEach, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { loginForm, fillOutLoginForm } from './utils';
import App from '../App';


const server = setupServer(
  http.post('http://localhost:8000/api/v1/auth/login/', () => {
    return HttpResponse.json({
      token_type: 'Bearer',
      access_token: 'access_token',
      access_token_expires_at: '2023-12-06T00:51:14.322Z',
      refresh_token: 'refresh_token',
      refresh_token_expires_at: '2023-12-06T00:51:14.322Z',
    });
  }),
  http.get('http://localhost:8000/api/v1/todo/list/', () => {
    return HttpResponse.json([
      {
        todo_list_id: '66135916-4fba-4551-b989-8e5f5dac540c',
        list_name: 'home',
        date_created: '2023-11-24T20:26:37.206000+00:00',
        date_modified: '2023-11-28T02:54:28.919000+00:00'
      },
      {
        todo_list_id: '8ba3da17-fae8-4481-bcff-c3b2380bc957',
        list_name: 'work',
        date_created: '2023-11-26T23:35:57.507000+00:00',
        date_modified: null
      },
      {
        todo_list_id: 'd85f6676-08e1-4f1d-b46b-b993917b3f92',
        list_name: 'groceries',
        date_created: '2023-11-26T23:47:52.102000+00:00',
        date_modified: null
      },
    ]);
  }),
  http.get('http://localhost:8000/api/v1/todo/task/', () => {
    return HttpResponse.json([
      {
        todo_id: '50c1c9b8-1804-4e6f-a477-de7b3ae28c0e',
        todo_list_id: '66135916-4fba-4551-b989-8e5f5dac540c',
        description: 'mow lawn',
        completed: false,
        date_created: '2023-11-26T19:10:01.953000+00:00',
        date_modified: '2023-11-26T19:16:18.573000+00:00'
      },
      {
        todo_id: '1b0aba51-dc5b-42f9-a149-854fcc4951d5',
        todo_list_id: '8ba3da17-fae8-4481-bcff-c3b2380bc957',
        description: 'tps report',
        completed: false,
        date_created: '2023-11-26T23:36:03.385000+00:00',
        date_modified: null
      },
      {
        todo_id: '04828c69-5f57-4656-a01c-589a26228157',
        todo_list_id: '8ba3da17-fae8-4481-bcff-c3b2380bc957',
        description: 'quarterly earnings',
        completed: true,
        date_created: '2023-11-26T23:37:09.396000+00:00',
        date_modified: '2023-11-26T23:37:09.396000+00:00'
      },
    ]);
  }),
  http.post('http://localhost:8000/api/v1/todo/list/', () => {
    return HttpResponse.json({
      todo_list_id: '554c910a-198b-44fd-9dce-41aba03273f1',
      list_name: 'yard',
      date_created: '2023-11-26T23:37:09.396000+00:00',
      date_modified: null,
    });
  }),
  http.put('http://localhost:8000/api/v1/todo/list/:todo_list_id', () => {
    return HttpResponse.json({
      todo_list_id: '554c910a-198b-44fd-9dce-41aba03273f1',
      list_name: 'yard',
      date_created: '2023-11-26T23:37:09.396000+00:00',
      date_modified: '2023-11-26T23:37:09.396000+00:00',
    });
  }),
  http.delete('http://localhost:8000/api/v1/todo/list/:todo_list_id', () => {
    return HttpResponse.json({
      todo_list_id: '554c910a-198b-44fd-9dce-41aba03273f1',
      list_name: 'yard',
      date_created: '2023-11-26T23:37:09.396000+00:00',
      date_modified: null,
    });
  }),
  http.post('http://localhost:8000/api/v1/todo/task/', () => {
    return HttpResponse.json({
      todo_id: 'f6a6074a-cb11-4617-a5e9-4cdf4df20503',
      todo_list_id: 'd85f6676-08e1-4f1d-b46b-b993917b3f92',
      description: 'apples',
      completed: false,
      date_created: '2023-11-26T23:37:09.396000+00:00',
      date_modified: null,
    });
  }),
  http.put('http://localhost:8000/api/v1/todo/task/:todo_id', () => {
    return HttpResponse.json({
      todo_id: 'f6a6074a-cb11-4617-a5e9-4cdf4df20503',
      todo_list_id: 'd85f6676-08e1-4f1d-b46b-b993917b3f92',
      description: 'apples',
      completed: false,
      date_created: '2023-11-26T23:37:09.396000+00:00',
      date_modified: '2023-11-26T23:37:09.396000+00:00',
    });
  }),
  http.delete('http://localhost:8000/api/v1/todo/task/:todo_id', () => {
    return HttpResponse.json({
      todo_id: 'f6a6074a-cb11-4617-a5e9-4cdf4df20503',
      todo_list_id: 'd85f6676-08e1-4f1d-b46b-b993917b3f92',
      description: 'apples',
      completed: false,
      date_created: '2023-11-26T23:37:09.396000+00:00',
      date_modified: null,
    });
  }),
);


beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());


beforeAll(() => {
  HTMLDialogElement.prototype.show = vi.fn();
  HTMLDialogElement.prototype.showModal = vi.fn();
  HTMLDialogElement.prototype.close = vi.fn();
});


async function navigateTodoPage(user) {
  const form = loginForm();
  await fillOutLoginForm(user, form);
  await user.click(form.loginButton);
}


async function initializeTodoPage() {
  const user = userEvent.setup();
  render(<App />);
  await navigateTodoPage(user);
  return user;
}


async function todoLists() {
  const lists = await screen.getAllByRole('list');
  const todoLists = lists[2];
  const listItems = within(todoLists).getAllByRole('listitem');
  return listItems;
}


function todoListForm() {
  const listNameField = screen.getByLabelText(/List Name/);
  const saveButton = screen.getByText('Save');

  return {
    listNameField,
    saveButton,
  }
}


async function fillOutTodoListForm(user, form) {
  await user.clear(form.listNameField);
  await user.type(form.listNameField, 'yard');
}


async function todos() {
  const todos = await screen.getByRole('table');
  const tableItems = within(todos).getAllByRole('row');
  return tableItems;
}


function todoForm() {
  const listNameField = screen.getByLabelText(/List Name/);
  const descriptionField = screen.getByLabelText(/Description/);
  const completedField = screen.getByLabelText(/Completed/);
  const saveButton = screen.getByText('Save');

  return {
    listNameField,
    descriptionField,
    completedField,
    saveButton,
  }
}


async function fillOutTodoForm(user, form) {
  await user.selectOptions(form.listNameField, 'groceries');
  await user.clear(form.descriptionField);
  await user.type(form.descriptionField, 'apples');
  await user.click(form.completedField);
}


test('has todo page', async () => {
  await initializeTodoPage();

  const pageTitle = screen.getByRole('heading', { level: 2 });

  expect(pageTitle).toHaveTextContent(/Todos/);
});


test('can view todo lists', async () => {
  await initializeTodoPage();

  const lists = await todoLists();

  expect(lists).toHaveLength(4);
  expect(lists[0]).toHaveTextContent(/[All]/);
  expect(lists[1]).toHaveTextContent(/home/);
  expect(lists[2]).toHaveTextContent(/work/);
  expect(lists[3]).toHaveTextContent(/groceries/);
});


test('first todo list is selected when lists exist', async () => {
  await initializeTodoPage();

  const lists = await todoLists();
  // first item (lists[0]) is [All] filter
  const firstList = within(lists[1]).queryByText('home');

  expect(firstList).toHaveAttribute('class', 'active cursor-pointer');
});


test('has message when no todo lists exist', async () => {
  server.use(
    http.get('http://localhost:8000/api/v1/todo/list/', () => {
      return HttpResponse.json([]);
    }),
    http.get('http://localhost:8000/api/v1/todo/task/', () => {
      return HttpResponse.json([]);
    }),
  );
  await initializeTodoPage();

  const lists = await todoLists();

  expect(lists).toHaveLength(1);
  expect(lists[0]).toHaveTextContent(/No Lists/);
});


test('can not see ALL lists filter item when no todo lists exist', async () => {
  server.use(
    http.get('http://localhost:8000/api/v1/todo/list/', () => {
      return HttpResponse.json([]);
    }),
    http.get('http://localhost:8000/api/v1/todo/task/', () => {
      return HttpResponse.json([]);
    }),
  );
  await initializeTodoPage();

  const lists = await todoLists();

  expect(lists).toHaveLength(1);
  expect(lists[0]).not.toHaveTextContent(/[All]/);
});


test('has create todo list', async () => {
  const user = await initializeTodoPage();

  const addTodoListButton = screen.getByRole('button', { name: '+ List' });
  await user.click(addTodoListButton);

  const modalTitle = await screen.queryByText(/Create List/);

  expect(modalTitle).toBeInTheDocument();
});


test('can cancel create todo list', async () => {
  const user = await initializeTodoPage();

  const addTodoListButton = screen.getByRole('button', { name: '+ List' });
  await user.click(addTodoListButton);

  const cancelButton = await screen.queryByText('Cancel');
  await user.click(cancelButton);

  const modalTitle = await screen.queryByText(/Create List/);

  expect(modalTitle).not.toBeInTheDocument();
});


test('create todo list form has required fields', async () => {
  const user = await initializeTodoPage();

  const addTodoListButton = screen.getByRole('button', { name: '+ List' });
  await user.click(addTodoListButton);

  const form = todoListForm();

  expect(form.listNameField).toBeInvalid();
  expect(form.saveButton).toBeDisabled();
});


test('can submit create todo list form after supplying list name', async () => {
  const user = await initializeTodoPage();

  const addTodoListButton = screen.getByRole('button', { name: '+ List' });
  await user.click(addTodoListButton);

  const form = todoListForm();
  await fillOutTodoListForm(user, form);

  expect(form.listNameField).toHaveValue('yard');
  expect(form.saveButton).toBeEnabled();
});


test('current todo list is still active after creating new list', async () => {
  const user = await initializeTodoPage();

  let lists = await todoLists();
  let workList = within(lists[2]).queryByText('work');
  await user.click(workList);

  const addTodoListButton = screen.getByRole('button', { name: '+ List' });
  await user.click(addTodoListButton);

  const form = todoListForm();
  await fillOutTodoListForm(user, form);
  await user.click(form.saveButton);
  
  lists = await todoLists();
  workList = within(lists[2]).queryByText('work');

  expect(workList).toHaveAttribute('class', 'active cursor-pointer');
});


test('adding todo list triggers data refresh', async () => {
  server.use(
    http.get('http://localhost:8000/api/v1/todo/list/', () => {
      return HttpResponse.json([]);
    }),
  );
  const user = await initializeTodoPage();

  const addTodoListButton = screen.getByRole('button', { name: '+ List' });
  await user.click(addTodoListButton);

  // saving todo list triggers data refresh
  server.use(
    http.get('http://localhost:8000/api/v1/todo/list/', () => {
      return HttpResponse.json([{
        todo_list_id: '554c910a-198b-44fd-9dce-41aba03273f1',
        list_name: 'yard',
        date_created: '2023-11-26T23:37:09.396000+00:00',
        date_modified: null,
      }]);
    }),
  );

  const form = todoListForm();
  await fillOutTodoListForm(user, form);
  await user.click(form.saveButton);
  
  const lists = await todoLists();

  expect(lists).toHaveLength(2);
  expect(lists[0]).toHaveTextContent(/[All]/);
  expect(lists[1]).toHaveTextContent(/yard/);
});


test('can edit todo list', async () => {
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const homeList = within(lists[1]).queryByText('home');
  await user.click(homeList);

  const modalTitle = await screen.queryByText(/Edit List/);

  expect(modalTitle).toBeInTheDocument();
});


test('can cancel edit todo list', async () => {
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const homeList = within(lists[1]).queryByText('home');
  await user.click(homeList);

  const cancelButton = await screen.queryByText('Cancel');
  await user.click(cancelButton);

  const modalTitle = await screen.queryByText(/Edit List/);

  expect(modalTitle).not.toBeInTheDocument();
});


test('edit todo list is prepopulated with list name', async () => {
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const homeList = within(lists[1]).queryByText('home');
  await user.click(homeList);

  const form = todoListForm();

  expect(form.listNameField).toHaveValue('home');
});


test('edit todo list form has required fields', async () => {
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const homeList = within(lists[1]).queryByText('home');
  await user.click(homeList);

  const form = todoListForm();
  await user.clear(form.listNameField);

  expect(form.listNameField).toBeInvalid();
  expect(form.saveButton).toBeDisabled();
});


test('can submit edit todo list form with list name', async () => {
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const homeList = within(lists[1]).queryByText('home');
  await user.click(homeList);

  const form = todoListForm();
  await fillOutTodoListForm(user, form);

  expect(form.listNameField).toHaveValue('yard');
  expect(form.saveButton).toBeEnabled();
});


test('current todo list is still active after being edited', async () => {
  const user = await initializeTodoPage();

  let lists = await todoLists();
  let workList = within(lists[2]).queryByText('work');
  await user.click(workList);
  await user.click(workList);

  server.use(
    http.get('http://localhost:8000/api/v1/todo/list/', () => {
      return HttpResponse.json([
        {
          todo_list_id: '66135916-4fba-4551-b989-8e5f5dac540c',
          list_name: 'home',
          date_created: '2023-11-24T20:26:37.206000+00:00',
          date_modified: '2023-11-28T02:54:28.919000+00:00'
        },
        {
          todo_list_id: '8ba3da17-fae8-4481-bcff-c3b2380bc957',
          list_name: 'yard',
          date_created: '2023-11-26T23:35:57.507000+00:00',
          date_modified: null
        },
        {
          todo_list_id: 'd85f6676-08e1-4f1d-b46b-b993917b3f92',
          list_name: 'groceries',
          date_created: '2023-11-26T23:47:52.102000+00:00',
          date_modified: null
        },
      ]);
    }),
  );

  const form = todoListForm();
  await fillOutTodoListForm(user, form);
  await user.click(form.saveButton);
  
  lists = await todoLists();
  workList = within(lists[2]).queryByText('yard');

  expect(workList).toHaveAttribute('class', 'active cursor-pointer');
});


test('editing todo list triggers data refresh', async () => {
  const user = await initializeTodoPage();

  let lists = await todoLists();
  const homeList = within(lists[1]).queryByText('home');
  await user.click(homeList);

  // saving todo list triggers data refresh
  server.use(
    http.get('http://localhost:8000/api/v1/todo/list/', () => {
      return HttpResponse.json([{
        todo_list_id: '554c910a-198b-44fd-9dce-41aba03273f1',
        list_name: 'yard',
        date_created: '2023-11-26T23:37:09.396000+00:00',
        date_modified: null,
      }]);
    }),
  );

  const form = todoListForm();
  await fillOutTodoListForm(user, form);
  await user.click(form.saveButton);
  
  lists = await todoLists();

  expect(lists).toHaveLength(2);
  expect(lists[0]).toHaveTextContent(/[All]/);
  expect(lists[1]).toHaveTextContent(/yard/);
});


test('can delete todo list', async () => {
  const user = await initializeTodoPage();

  let lists = await todoLists();
  const homeList = within(lists[1]).queryByText('home');
  await user.click(homeList);

  const deleteButton = screen.queryByText('Delete');

  expect(deleteButton).toBeInTheDocument();
});


test('deleting todo list triggers data refresh', async () => {
  const user = await initializeTodoPage();

  let lists = await todoLists();
  const homeList = within(lists[1]).queryByText('home');
  await user.click(homeList);

  // deleting todo list triggers data refresh
  server.use(
    http.get('http://localhost:8000/api/v1/todo/list/', () => {
      return HttpResponse.json([
        {
          todo_list_id: '8ba3da17-fae8-4481-bcff-c3b2380bc957',
          list_name: 'work',
          date_created: '2023-11-26T23:35:57.507000+00:00',
          date_modified: null
        },
        {
          todo_list_id: 'd85f6676-08e1-4f1d-b46b-b993917b3f92',
          list_name: 'groceries',
          date_created: '2023-11-26T23:47:52.102000+00:00',
          date_modified: null
        },
      ]);
    }),
  );

  const deleteButton = screen.getByText('Delete');
  await user.click(deleteButton);

  lists = await todoLists();

  expect(lists).toHaveLength(3);
  expect(lists[0]).toHaveTextContent(/[All]/);
  expect(lists[1]).toHaveTextContent(/work/);
  expect(lists[2]).toHaveTextContent(/groceries/);
});


test('can add todo if lists exist', async () => {
  await initializeTodoPage();

  const addTodoButton = screen.queryByRole('button', { name: '+ Todo' });

  expect(addTodoButton).toBeInTheDocument();
});


test('can not add todo if no lists exist', async () => {
  server.use(
    http.get('http://localhost:8000/api/v1/todo/list/', () => {
      return HttpResponse.json([]);
    }),
    http.get('http://localhost:8000/api/v1/todo/task/', () => {
      return HttpResponse.json([]);
    }),
  );
  await initializeTodoPage();

  const addTodoButton = screen.queryByRole('button', { name: '+ Todo' });

  expect(addTodoButton).not.toBeInTheDocument();
});


test('can view todos for default first list', async () => {
  await initializeTodoPage();

  const content = await todos();

  expect(content).toHaveLength(2);
  expect(content[0]).toHaveTextContent(/Description/);
  expect(content[0]).toHaveTextContent(/Completed/);
  expect(content[1]).toHaveTextContent(/mow lawn/);
});


test('can view todos for selected list', async () => {
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const workList = within(lists[2]).queryByText('work');
  await user.click(workList);

  const content = await todos();

  expect(content).toHaveLength(3);
  expect(content[0]).toHaveTextContent(/Description/);
  expect(content[0]).toHaveTextContent(/Completed/);
  expect(content[1]).toHaveTextContent(/tps report/);
  expect(content[2]).toHaveTextContent(/quarterly earnings/);
});


test('has message when no todos exist for list', async () => {
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const groceriesList = within(lists[3]).queryByText('groceries');
  await user.click(groceriesList);

  const content = await todos();

  expect(content).toHaveLength(2);
  expect(content[0]).toHaveTextContent(/Description/);
  expect(content[0]).toHaveTextContent(/Completed/);
  expect(content[1]).toHaveTextContent(/No todos/);
});


test('can view all todos', async () => {
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const allList = within(lists[0]).queryByText('[All]');
  await user.click(allList);

  const content = await todos();

  expect(content).toHaveLength(4);
  expect(content[0]).toHaveTextContent(/Description/);
  expect(content[0]).toHaveTextContent(/Completed/);
  expect(content[1]).toHaveTextContent(/mow lawn/);
  expect(content[2]).toHaveTextContent(/tps report/);
  expect(content[3]).toHaveTextContent(/quarterly earnings/);
});


test('shows todo progress', async () => {
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const workList = within(lists[2]).queryByText('work');
  await user.click(workList);

  const content = await todos();
  const incompleteTask = within(content[1]).getByRole('checkbox');
  const completeTask = within(content[2]).getByRole('checkbox');

  expect(incompleteTask).not.toBeChecked();
  expect(completeTask).toBeChecked();
});


test('has message when no todos exist for any list when viewing all', async () => {
  server.use(
    http.get('http://localhost:8000/api/v1/todo/task/', () => {
      return HttpResponse.json([]);
    }),
  );
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const allList = within(lists[0]).queryByText('[All]');
  await user.click(allList);

  const content = await todos();

  expect(content).toHaveLength(2);
  expect(content[0]).toHaveTextContent(/Description/);
  expect(content[0]).toHaveTextContent(/Completed/);
  expect(content[1]).toHaveTextContent(/No todos/);
});


test('can hide completed todos', async () => {
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const workList = within(lists[2]).queryByText('work');
  await user.click(workList);

  const allWorkListContent = await todos();

  // hide completed checkbox triggers call to server for incomplete todos
  server.use(
    http.get('http://localhost:8000/api/v1/todo/task/', () => {
      return HttpResponse.json([
        {
          todo_id: '50c1c9b8-1804-4e6f-a477-de7b3ae28c0e',
          todo_list_id: '66135916-4fba-4551-b989-8e5f5dac540c',
          description: 'mow lawn',
          completed: false,
          date_created: '2023-11-26T19:10:01.953000+00:00',
          date_modified: '2023-11-26T19:16:18.573000+00:00'
        },
        {
          todo_id: '1b0aba51-dc5b-42f9-a149-854fcc4951d5',
          todo_list_id: '8ba3da17-fae8-4481-bcff-c3b2380bc957',
          description: 'tps report',
          completed: false,
          date_created: '2023-11-26T23:36:03.385000+00:00',
          date_modified: null
        },
      ]);
    }),
  );

  const hideCompletedCheckbox = screen.getByLabelText(/Hide completed/);
  await user.click(hideCompletedCheckbox);

  const incompleteWorkListContent = await todos();

  expect(hideCompletedCheckbox).toBeChecked();

  expect(allWorkListContent).toHaveLength(3);
  expect(allWorkListContent[1]).toHaveTextContent(/tps report/);
  expect(allWorkListContent[2]).toHaveTextContent(/quarterly earnings/);

  expect(incompleteWorkListContent).toHaveLength(2);
  expect(incompleteWorkListContent[1]).toHaveTextContent(/tps report/);
});


test('has create todo', async () => {
  const user = await initializeTodoPage();

  const addTodoButton = screen.getByRole('button', { name: '+ Todo' });
  await user.click(addTodoButton);

  const modalTitle = await screen.queryByText(/Create Todo/);

  expect(modalTitle).toBeInTheDocument();
});


test('can cancel create todo', async () => {
  const user = await initializeTodoPage();

  const addTodoButton = screen.getByRole('button', { name: '+ Todo' });
  await user.click(addTodoButton);

  const cancelButton = await screen.queryByText('Cancel');
  await user.click(cancelButton);

  const modalTitle = await screen.queryByText(/Create Todo/);

  expect(modalTitle).not.toBeInTheDocument();
});


test('create todo form has required fields', async () => {
  const user = await initializeTodoPage();

  const addTodoButton = screen.getByRole('button', { name: '+ Todo' });
  await user.click(addTodoButton);

  const form = todoForm();

  expect(form.descriptionField).toBeInvalid();
  expect(form.saveButton).toBeDisabled();
});


test('can submit create todo form after supplying description', async () => {
  const user = await initializeTodoPage();

  const addTodoButton = screen.getByRole('button', { name: '+ Todo' });
  await user.click(addTodoButton);

  const form = todoForm();
  await fillOutTodoForm(user, form);

  expect(form.descriptionField).toHaveValue('apples');
  expect(form.saveButton).toBeEnabled();
});


test('adding todo triggers data refresh', async () => {
  const user = await initializeTodoPage();

  const lists = await todoLists();
  const groceriesList = within(lists[3]).queryByText('groceries');
  await user.click(groceriesList);

  const addTodoButton = screen.getByRole('button', { name: '+ Todo' });
  await user.click(addTodoButton);

  // adding todo triggers data refresh
  server.use(
    http.get('http://localhost:8000/api/v1/todo/task/', () => {
      return HttpResponse.json([
        {
          todo_id: 'f6a6074a-cb11-4617-a5e9-4cdf4df20503',
          todo_list_id: 'd85f6676-08e1-4f1d-b46b-b993917b3f92',
          description: 'apples',
          completed: false,
          date_created: '2023-11-26T23:37:09.396000+00:00',
          date_modified: null,
        },
      ]);
    }),
  );

  const form = todoForm();
  await fillOutTodoForm(user, form);
  await user.click(form.saveButton);

  const content = await todos();

  expect(content).toHaveLength(2);
  expect(content[0]).toHaveTextContent(/Description/);
  expect(content[0]).toHaveTextContent(/Completed/);
  expect(content[1]).toHaveTextContent(/apples/);
});


test('can edit todo', async () => {
  const user = await initializeTodoPage();

  const content = await todos();
  const firstTodo = within(content[1]).queryByText('mow lawn');
  await user.click(firstTodo);

  const modalTitle = await screen.queryByText(/Edit Todo/);

  expect(modalTitle).toBeInTheDocument();
});


test('can cancel edit todo', async () => {
  const user = await initializeTodoPage();

  const content = await todos();
  const firstTodo = within(content[1]).queryByText('mow lawn');
  await user.click(firstTodo);

  const cancelButton = await screen.queryByText('Cancel');
  await user.click(cancelButton);

  const modalTitle = await screen.queryByText(/Edit Todo/);

  expect(modalTitle).not.toBeInTheDocument();
});


test('edit todo is prepopulated with todo data', async () => {
  const user = await initializeTodoPage();

  const content = await todos();
  const firstTodo = within(content[1]).queryByText('mow lawn');
  await user.click(firstTodo);

  const form = todoForm();

  expect(form.listNameField).toHaveDisplayValue('home');
  expect(form.descriptionField).toHaveValue('mow lawn');
  expect(form.completedField).not.toBeChecked();
});


test('edit todo form has required fields', async () => {
  const user = await initializeTodoPage();

  const content = await todos();
  const firstTodo = within(content[1]).queryByText('mow lawn');
  await user.click(firstTodo);

  const form = todoForm();
  await user.clear(form.descriptionField);

  expect(form.descriptionField).toBeInvalid();
  expect(form.saveButton).toBeDisabled();
});


test('can submit edit todo form after supplying description', async () => {
  const user = await initializeTodoPage();

  const content = await todos();
  const firstTodo = within(content[1]).queryByText('mow lawn');
  await user.click(firstTodo);

  const form = todoForm();
  await fillOutTodoForm(user, form);

  expect(form.listNameField).toHaveDisplayValue('groceries');
  expect(form.descriptionField).toHaveValue('apples');
  expect(form.completedField).toBeChecked();
  expect(form.saveButton).toBeEnabled();
});


test('editing todo triggers data refresh', async () => {
  const user = await initializeTodoPage();

  let content = await todos();
  const firstTodo = within(content[1]).queryByText('mow lawn');
  await user.click(firstTodo);

  // editing todo triggers data refresh
  server.use(
    http.get('http://localhost:8000/api/v1/todo/task/', () => {
      return HttpResponse.json([
        {
          todo_id: 'f6a6074a-cb11-4617-a5e9-4cdf4df20503',
          todo_list_id: 'd85f6676-08e1-4f1d-b46b-b993917b3f92',
          description: 'apples',
          completed: false,
          date_created: '2023-11-26T23:37:09.396000+00:00',
          date_modified: null,
        },
      ]);
    }),
  );

  const form = todoForm();
  await fillOutTodoForm(user, form);
  await user.click(form.saveButton);

  content = await todos();

  expect(content).toHaveLength(2);
  expect(content[0]).toHaveTextContent(/Description/);
  expect(content[0]).toHaveTextContent(/Completed/);
  expect(content[1]).toHaveTextContent(/No todos/);
});


test('can delete todo', async () => {
  const user = await initializeTodoPage();

  let content = await todos();
  const firstTodo = within(content[1]).queryByText('mow lawn');
  await user.click(firstTodo);

  const deleteButton = screen.queryByText('Delete');

  expect(deleteButton).toBeInTheDocument();
});


test('deleting todo triggers data refresh', async () => {
  const user = await initializeTodoPage();

  let content = await todos();
  const firstTodo = within(content[1]).queryByText('mow lawn');
  await user.click(firstTodo);

  // deleting todo triggers data refresh
  server.use(
    http.get('http://localhost:8000/api/v1/todo/task/', () => {
      return HttpResponse.json([]);
    }),
  );

  const deleteButton = screen.queryByText('Delete');
  await user.click(deleteButton);

  content = await todos();

  expect(content).toHaveLength(2);
  expect(content[0]).toHaveTextContent(/Description/);
  expect(content[0]).toHaveTextContent(/Completed/);
  expect(content[1]).toHaveTextContent(/No todos/);
});


// todo: impl, view/create/edit/delete list/todo
// test('backend issue request', async () => {
// });


// todo: impl, view/create/edit/delete list/todo
// test('error api call', async () => {
// });
