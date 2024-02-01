const JSON_CONTENT_TYPE = 'application/json; charset=UTF-8';
const FORM_CONTENT_TYPE = 'application/x-www-form-urlencoded';


export function stateListControlFactory(setState) {
  function add(item) {
    if (!('id' in item)) {
      item.id = Math.random();
    }
    setState(prevState => [...prevState, item]);
    return item;
  }

  function create() {
    return add({});
  }

  function remove(item) {
    setState(prevState => [...prevState.filter(s => s.id !== item.id)]);
  }

  return {
    create,
    add,
    remove,
  }
}


function snakeToCamel(snakeCase) {
  return snakeCase.split('_')
    .map((t, i) => i === 0 ? t : t.charAt(0).toUpperCase() + t.substring(1))
    .reduce((a, c) => a + c);
}


function camelToSnake(camelCase) {
  return camelCase.charAt(0).toLowerCase() +
    camelCase.substring(1).replace(/[A-Z]/g, c => `_${c.toLowerCase()}`);
}


function objKeyMutate(obj, mutate) {
  return Object.assign(...Object.keys(obj).map(k => ({[mutate(k)]: obj[k]})));
}


function objCamelToSnake(obj) {
  return objKeyMutate(obj, camelToSnake);
}


function objSnakeToCamel(obj) {
  return objKeyMutate(obj, snakeToCamel);
}


async function processResponse(response) {
  const result = {};
  const data = await response.json();

  if (response.ok) {
    if (Array.isArray(data)) {
      result.data = data.map(d => objSnakeToCamel(d));
    } else {
      result.data = objSnakeToCamel(data);
    }
  } else if (response.status === 422) {
    console.log('422 response: ', data);
    result.errors = data.detail.map(d => `${d.loc.length > 1 ? d.loc[1] : d.loc}: ${d.msg}`);
  } else {
    console.log('non ok response: ', data);
    const msg = data.message ? data.message : "server error";
    result.errors = [`Issue occurred during request: ${msg}`];
  }

  return result;
}


export async function getApi(url, authToken) {
  const headers = {
    'accept': 'application/json'
  }

  if (authToken) {
    Object.assign(headers, {Authorization: `${authToken.tokenType} ${authToken.accessToken}`})
  }

  const response = await fetch(url, {
    method: 'GET',
    headers,
  });
  const result = await processResponse(response);

  return result;
}


async function mutateApi(method, url, request, isJson, authToken) {
  const headers = {
    'accept': 'application/json',
  }

  const fetchParams = {
    method,
    headers,
  }

  if (request) {
    const converted_req = objCamelToSnake(request);
    const body = isJson ? JSON.stringify(converted_req) : new URLSearchParams(converted_req);
    Object.assign(fetchParams, {body,});

    const contentType = isJson ? JSON_CONTENT_TYPE : FORM_CONTENT_TYPE;
    Object.assign(headers, {'Content-type': contentType});
  }

  if (authToken) {
    Object.assign(headers, {Authorization: `${authToken.tokenType} ${authToken.accessToken}`});
  }

  const response = await fetch(url, fetchParams);
  const result = await processResponse(response);

  return result;
}


export async function postApi(url, request, isJson, authToken) {
  return await mutateApi('POST', url, request, isJson, authToken);
}


export async function putApi(url, request, isJson, authToken) {
  return await mutateApi('PUT', url, request, isJson, authToken);
}


export async function deleteApi(url, authToken) {
  return await mutateApi('DELETE', url, null, null, authToken);
}
