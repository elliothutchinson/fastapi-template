import { API_V1_URL } from '../common/contants';
import { postApi } from '../common/utils';


export async function loginUser(userLogin) {
  const url = `${API_V1_URL}/auth/login/`;
  let result = {};
  try {
    result = await postApi(url, userLogin, false);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred during login.'];
  }
  return result;
}
