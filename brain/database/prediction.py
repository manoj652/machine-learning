#!/usr/bin/python

'''

This file saves previous predictions.

'''

import json
from flask import current_app, session
from brain.database.query import SQL


class Prediction(object):
    '''

    This class provides an interface to save, a previous generated svm or svr
    prediction result.

    Note: this class explicitly inherits the 'new-style' class.

    '''

    def __init__(self):
        '''

        This constructor is responsible for defining class variables.

        '''

        self.list_error = []
        self.sql = SQL()
        self.db_ml = current_app.config.get('DB_ML')
        if session.get('uid'):
            self.uid = int(session.get('uid'))
        else:
            self.uid = 0

    def save(self, payload, model_type, title):
        '''

        This method stores the corresponding prediction.

        @sql_statement, is a sql format string, and not a python string.
            Therefore, '%s' is used for argument substitution.

        Note: 'UTC_TIMESTAMP' returns the universal UTC datetime

        '''

        # local variables
        data = json.loads(payload)
        result = data['result']

        # insert prediction
        self.sql.connect(self.db_ml)

        if model_type == 'svm':
            classes = data['classes']
            probability = data['probability']
            decision_function = data['decision_function']

            # svm results
            sql_statement = 'INSERT INTO tbl_svm_results '\
                '(title, result, uid_created, datetime_created) '\
                'VALUES(%s, %s, %s, UTC_TIMESTAMP())'
            args = (title, result, self.uid)
            svm_results = self.sql.execute(
                sql_statement,
                'insert',
                args,
            )

            # svm classes
            for x in classes:
                sql_statement = 'INSERT INTO tbl_svm_results_class '\
                    '(id_result, class) VALUES(%s, %s)'
                args = (svm_results['id'], x)
                self.sql.execute(sql_statement, 'insert', args,)

            # svm probability
            for x in probability:
                sql_statement = 'INSERT INTO tbl_svm_results_probability '\
                    '(id_result, probability) VALUES(%s, %s)'
                args = (svm_results['id'], x)
                self.sql.execute(sql_statement, 'insert', args,)

            # svm decision function
            for x in decision_function:
                sql_statement = 'INSERT INTO tbl_svm_results_decision_function '\
                    '(id_result, decision_function) VALUES(%s, %s)'
                args = (svm_results['id'], x,)
                self.sql.execute(sql_statement, 'insert', args,)

        elif model_type == 'svr':
            # svr results
            sql_statement = 'INSERT INTO tbl_svr_results '\
                '(title, result, uid_created, datetime_created) '\
                'VALUES(%s, %s, %s, UTC_TIMESTAMP())'
            args = (title, result, self.uid)
            svr_results = self.sql.execute(
                sql_statement,
                'insert',
                args,
            )

            # svr r2
            sql_statement = 'INSERT INTO tbl_svr_results_r2 '\
                '(id_result, r2) VALUES(%s, %s)'
            args = (svr_results['id'], data['r2'])
            self.sql.execute(sql_statement, 'insert', args,)

        # retrieve any error(s), disconnect from database
        response_error = self.sql.get_errors()
        self.sql.disconnect()

        # return result
        if response_error:
            return {'error': response_error, 'result': 1}
        else:
            return {'error': None, 'result': 0}

    def get_all_titles(self, model_type=None):
        '''

        This method retrieves all stored predictions for the current user.

        @sql_statement, is a sql format string, and not a python string.
            Therefore, '%s' is used for argument substitution.

        '''

        # select prediction
        self.sql.connect(self.db_ml)

        if model_type == 'svm':
            sql_statement = 'SELECT title, datetime_created ' \
                'FROM tbl_svm_results '\
                'WHERE uid_created=%s'
            args = (self.uid)
            response = self.sql.execute(sql_statement, 'select', args)

        elif model_type == 'svr':
            sql_statement = 'SELECT title, datetime_created ' \
                'FROM tbl_svr_results '\
                'WHERE uid_created=%s'
            args = (self.uid)
            response = self.sql.execute(sql_statement, 'select', args)

        else:
            sql_statement = 'SELECT tbl_svm_results.title, '\
                'tbl_svm_results.datetime_created, ' \
                'tbl_svr_results.title, '\
                'tbl_svr_results.datetime_created '\
                'FROM tbl_svm_results JOIN tbl_svr_results '\
                'ON tbl_svm_results.id = tbl_svr_results.id '\
                'WHERE tbl_svm_results.uid_created=%s '\
                'AND tbl_svr_results.uid_created=%s '\
            args = (self.uid, self.uid)
            response = self.sql.execute(sql_statement, 'select', args)

        # retrieve any error(s), disconnect from database
        response_error = self.sql.get_errors()
        self.sql.disconnect()

        # return result
        if response_error:
            return {
                'status': False,
                'error': response_error,
                'result': None
            }
        else:
            return {
                'status': True,
                'error': None,
                'result': response['result'],
            }
