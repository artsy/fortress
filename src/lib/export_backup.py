from pathlib import Path


def write_file(output_file, data, data_format='text', heading=None, mode=0o600, exist_ok=True):
  ''' write text or binary data to file, create file with proper permissions '''
  if data_format == 'text':
    write_text_file(output_file, data, heading, mode, exist_ok)
  elif data_format == 'binary':
    write_binary_file(output_file, data, mode, exist_ok)
  else:
    raise Exception(f'Un-supported data format: {data_format}')

def write_text_file(output_file, data, heading=None, mode=0o600, exist_ok=True):
  ''' write heading and text data to output file, create file with proper permissions '''
  fobj = Path(output_file)
  fobj.touch(mode=mode, exist_ok=exist_ok)
  with open(output_file, 'w') as f:
    if heading:
      f.write(heading)
    f.write(data)

def write_binary_file(output_file, data, mode=0o600, exist_ok=True):
  ''' write binary data to output file, create file with proper permissions '''
  fobj = Path(output_file)
  fobj.touch(mode=mode, exist_ok=exist_ok)
  with open(output_file, 'wb') as f:
    f.write(data)
