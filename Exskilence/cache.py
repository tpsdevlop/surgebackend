from django.core.cache import cache
def create_cache( key , value , time):
    if value == None:
        return
    cache.set( key , value , 60 )
    return

def get_cache( key ):
    return cache.get( key )