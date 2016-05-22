import re

class RouteCondition:
    def __init__(self, condition_type, condition_value):
        self.condition_type = condition_type
        if self.condition_type in ['path_info', 'path_start'] and condition_value[0:1] != '/':
            condition_value = '/' + condition_value
        self.condition_value = condition_value

    def eval_condition(self, request):
        if self.condition_type in ['path_info', 'request_method', 'remote_address']:

            if getattr(request, self.condition_type) == self.condition_value:
                return True
            return False

        elif self.condition_type == 'path_in_array':

            if request.path_info[1:] in self.condition_value:
                return True
            return False

        elif self.condition_type == 'path_start':
            path_len = len(self.condition_value)
            if request.path_info[0:path_len] == self.condition_value:
                return True
            return False

        elif self.condition_type == 'path_end':
            path_len = len(self.condition_value)
            if request.path_info[(-1 * path_len):] == self.condition_value:
                return True
            return False

        elif self.condition_type == 'path_regex':
            if re.match(self.condition_value, request.path_info):
                return True
            return False

        elif self.condition_type == 'any':
            return True


class Route:
    def __init__(self, conditions, func=None):
        self.conditions = []
        if type(conditions) is not list:
            condition = self.parse_condition(conditions)
            if condition:
                self.conditions.append(RouteCondition(condition['condition_type'], condition['condition_value']))
            else:
                print 'Bad condition: {}'.format(conditions)
        elif type(conditions) is list:
            for c in conditions:
                condition = self.parse_condition(c)
                if condition:
                    self.conditions.append(RouteCondition(condition['condition_type'], condition['condition_value']))
                else:
                    print "Bad condition: {}".format(c)
        self.func = func

    def eval_conditions(self, request):
        for c in self.conditions:
            if not c.eval_condition(request):
                return False
        return True

    @staticmethod
    def parse_condition(condition):
        if type(condition) is dict:
            if 'condition_type' in condition.keys() and 'condition_value' in condition.keys():
                return condition
            elif len(condition) == 1:
                cond_type = condition.keys()[0]
                return {'condition_type': cond_type, 'condition_value': condition[cond_type]}
        elif type(condition) is str:
            if condition == 'any':
                return {'condition_type': 'any', 'condition_value': ''}
        else:
            return False


class RouteTable:
    def __init__(self):
        self.route_table = []

    def add_route(self, conditions, func):
        self.route_table.append(Route(conditions, func))

    def eval_route(self, request):
        for route in self.route_table:
            if route.eval_conditions(request):
                return route.func
        return False
