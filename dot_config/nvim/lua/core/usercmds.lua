vim.api.nvim_create_user_command('NewDailyPersonal', function()
  local filename = '~/Repos/notes/personal/daily/' .. os.date('%Y-%m-%d') .. '.md'
  vim.cmd('e ' .. filename)
end, {})

vim.api.nvim_create_user_command('NewDailyWork', function()
  local filename = '~/Repos/notes/work/daily/' .. os.date('%Y-%m-%d') .. '.md'
  vim.cmd('e ' .. filename)
end, {})
