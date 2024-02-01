import { API_V1_URL } from '../common/contants';
import { postApi } from '../common/utils';


export async function registerUser(userCreate) {
  const url = `${API_V1_URL}/user/`;
  let result = {};
  try {
    result = await postApi(url, userCreate, true, null);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred during registration.'];
  }
  return result;
}
