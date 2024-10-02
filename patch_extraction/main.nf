process RUN_MODEL {
  conda 'environment.yml'

  """
  python your_script.py
  """
}

workflow {
  RUN_MODEL()
}
