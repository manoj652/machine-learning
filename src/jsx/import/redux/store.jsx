/**
 * store.jsx: create consistent redux state tree.
 *
 * Note: importing 'named export' (multiple export statements in a module),
 *       requires the object being imported, to be surrounded by { brackets }.
 *
 * Note: when debugging in this script, either implement 'middleware', or add
 *       the following after the 'store' definition:
 *
 *       // manual console trace
 *         store.subscribe(() => {
 *             console.log('store changed', store.getState());
 *         })
 *
 */

import { createStore } from 'redux';
import storageMiddleware from './reducer/login-reducer.jsx';

// redux store: entire state tree for the application
const store = createStore(
    storageMiddleware,
    {username: sessionStorage.getItem('username') || 'anonymous'}
);

// indicate which class can be exported, and instantiated via 'require'
export default store
