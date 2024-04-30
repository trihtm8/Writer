class Err:
    s = 'status'
    e = 'err'
    d = 'detail'

    def none(seft):
        return {
            seft.e: False,
            seft.d: 'Success'
        }

    def unsuportedMethod(seft):
        return {
            seft.e: True,
            seft.d: 'Unsupported method!'
        }

    def objectDoesNotExists(seft, obj_name):
        return {
            seft.e: True,
            seft.d: str(obj_name) + ' does not exists'
        }

    def permissionDeny(seft):
        return {
            seft.e: True,
            seft.d: 'Permission deny'
        }

    def requiredVariable(seft, var_name):
        return {
            seft.e: True,
            seft.d: 'Required '+str(var_name)
        }

    def requiredLogin(seft):
        return {
            seft.e: True,
            seft.d: 'You must login'
        }

    def requiredLogout(seft):
        return {
            seft.e: True,
            seft.d: 'You must logout'
        }
    
    def alreadyExists(seft, objectClass):
        return {
            seft.e: True,
            seft.d: 'This ' + str(objectClass) + " alredy exists"
        }
    
    def ortherErr(seft, detail):
        return{
            seft.e : True,
            seft.d : detail
        }