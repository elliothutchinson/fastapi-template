import { API_V1_URL } from '../common/contants';
import { getApi, putApi } from '../common/utils';


export async function fetchProfile(authToken) {
  const url = `${API_V1_URL}/user/`;
  let result = {};
  try {
    result = await getApi(url, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred during login.'];
  }
  return result;
}


export async function updateProfile(userUpdate, authToken) {
  const url = `${API_V1_URL}/user/`;
  let result = {};
  try {
    result = await putApi(url, userUpdate, true, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred during profile update.'];
  }
  return result;
}


export async function changePassword(passwordChange, authToken) {
  const url = `${API_V1_URL}/user/`;
  let result = {};
  try {
    result = await putApi(url, passwordChange, true, authToken);
  } catch (error) {
    console.log('error: ', error);
    result.errors = ['Error occurred during password change.'];
  }
  return result;
}
