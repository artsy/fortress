def is_artsy_staging_internal_hostname(name):
  ''' return true if name ends with stg.artsy.systems'''
  return name.endswith('stg.artsy.systems')

def is_artsy_production_internal_hostname(name):
  ''' return true if name ends with prd.artsy.systems'''
  return name.endswith('prd.artsy.systems')

def hostname_agrees_with_environment(name, env):
  '''
  return true if environment is staging and
  name is artsy staging internal hostname,
  similarly for production
  '''
  if env == 'staging':
    return is_artsy_staging_internal_hostname(name)
  elif env == 'production':
    return is_artsy_production_internal_hostname(name)
  else:
    raise Exception(f'Unknown Artsy environment: {env}')
