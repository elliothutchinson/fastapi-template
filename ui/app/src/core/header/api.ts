import { API_V1_URL } from '../common/contants';
import { postApi } from '../common/utils';


export async function logoutUser(authToken) {
  const url = `${API_V1_URL}/auth/logout/`;
  let result = {};
  try {
    result = await postApi(url, authToken, true, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred during logout.'];
  }
  return result;
}
