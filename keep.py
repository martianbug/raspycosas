import gkeepapi

keep = gkeepapi.Keep()
success = keep.login('m.serranojuste@gmail.com', 'PORTATIL')

note = keep.createNote('Todo', 'Eat breakfast')
note.pinned = True
note.color = gkeepapi.node.ColorValue.Red
keep.sync()