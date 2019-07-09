
def delete_files(sender, **kwargs):
    kwargs['instance'].minimap.delete()
    kwargs['instance'].file.delete()
