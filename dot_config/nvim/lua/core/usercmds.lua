vim.api.nvim_create_user_command('NewPersonalNote', function(opts)
  local full_path = '~/Repos/notes/personal/misc/' .. opts.args .. '.md'
  vim.cmd('e ' .. full_path)
end, { nargs = 1, desc = 'Filename' })

vim.api.nvim_create_user_command('NewWorkNote', function(opts)
  local full_path = '~/Repos/notes/work/misc/' .. opts.args .. '.md'
  vim.cmd('e ' .. full_path)
end, { nargs = 1, desc = 'Filename' })

vim.api.nvim_create_user_command('NewPersonalToDo', function(opts)
  local filename = opts.args ~= '' and opts.args or os.date('%Y-%m-%d')
  local full_path = '~/Repos/notes/personal/daily/' .. filename .. '.md'
  vim.cmd('e ' .. full_path)
end, { nargs = '?', desc = 'Filename' })

vim.api.nvim_create_user_command('NewWorkToDo', function(opts)
  local filename = opts.args ~= '' and opts.args or os.date('%Y-%m-%d')
  local full_path = '~/Repos/notes/work/daily/' .. filename .. '.md'
  vim.cmd('e ' .. full_path)
end, { nargs = '?', desc = 'Filename' })
