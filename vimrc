call plug#begin('~/.vim/plugged')

Plug 'altercation/vim-colors-solarized'
Plug 'ctrlpvim/ctrlp.vim'
Plug 'elixir-lang/vim-elixir'
Plug 'janko-m/vim-test'
Plug 'kchmck/vim-coffee-script'
Plug 'keith/swift.vim'
Plug 'pbrisbin/vim-mkdir'
Plug 'scrooloose/syntastic'
Plug 'SirVer/ultisnips' | Plug 'honza/vim-snippets'
Plug 'tpope/vim-bundler'
Plug 'tpope/vim-endwise'
Plug 'tpope/vim-fugitive'
Plug 'tpope/vim-ragtag'
Plug 'tpope/vim-rails'
Plug 'tpope/vim-repeat'
Plug 'tpope/vim-sensible'
Plug 'tpope/vim-surround'
Plug 'tpope/vim-unimpaired'
Plug 'fatih/vim-go', { 'do': ':GoUpdateBinaries' }

" supress python warning
" https://github.com/vim/vim/issues/3117#issuecomment-406853295
if !has('patch-8.1.201')
  silent! python3 1
endif
Plug 'Valloric/YouCompleteMe'

Plug 'vim-ruby/vim-ruby'
Plug 'vim-scripts/tComment'

call plug#end()

" we now return to your regularly scheduled .vimrc
let mapleader = ','
set nocompatible

" backup files
set backupdir=~/.vim/tmp
set directory=~/.vim/tmp

" solarized setup
let g:solarized_termcolors=256
set background=dark
colorscheme solarized

" display customization
set number
set encoding=utf-8
set cursorline
set list

" statusline originally from janus
set statusline=%f\ %m\ %r
set statusline+=Line:%l/%L[%p%%]
set statusline+=Col:%v
set statusline+=Buf:#%n
set statusline+=[%b][0x%B]
set statusline+=%{fugitive#statusline()}

" tabbing ish
set tabstop=2
set shiftwidth=2
set expandtab
set shiftround

" where to open splits
set splitbelow
set splitright

" don't add comment prefix when opening new lines
set formatoptions-=o

" searching
set hlsearch
set ignorecase
set smartcase

" yank to system clipboard
set clipboard=unnamed

" override javascript commenting
let g:tcomment_types = {
  \ 'javascript': '// %s',
  \ 'javascript_inline': '// %s',
  \ 'javascript_block': '// %s',
  \ 'javaScript': '// %s',
  \ 'javaScript_inline': '// %s',
  \ 'javaScript_block': '// %s',
  \ }

" don't manage working directory
let g:ctrlp_working_path_mode = 0

" ctrlp ignores
let g:ctrlp_custom_ignore = {
  \ 'dir': 'build$\|\.git$\|\.storyboardc$\|\.svn$\|target$\|\.unpack$\|vendor$\|tmp/cache$\|ib\.xcodeproj$',
  \ 'file': 'ctags$\|\.ccignore$\|\.DS_Store$\|\.gitignore$\|\.repl_history$',
  \ 'link': '',
  \ }

" open multiple files in separate tabs
let g:ctrlp_open_multiple_files = 't'

let g:ctrlp_user_command = ['.git', 'cd %s && git ls-files . -co --exclude-standard', 'find %s -type f']

" `git ls-files` is fast enough that CtrlP doesn't need to cache
let g:ctrlp_use_caching = 0

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Thank you, Gary
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" Clear the search buffer when hitting return
function! MapCR()
  nnoremap <cr> :nohlsearch<cr>
endfunction
call MapCR()

" jump to alternate file
nnoremap <leader><leader> <c-^>

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" MULTIPURPOSE TAB KEY
" Indent if we're at the beginning of a line. Else, do completion.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
function! InsertTabWrapper()
  let col = col('.') - 1
  if !col || getline('.')[col - 1] !~ '\k'
    return "\<tab>"
  else
    return "\<c-p>"
  endif
endfunction
inoremap <tab> <c-r>=InsertTabWrapper()<cr>
inoremap <s-tab> <c-n>

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" OPEN FILES IN DIRECTORY OF CURRENT FILE
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
cnoremap %% <C-R>=expand('%:h').'/'<cr>
map <leader>e :edit %%
map <leader>v :vsplit %%

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" RENAME CURRENT FILE
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
function! RenameFile()
  let old_name = expand('%')
  let new_name = input('New file name: ', expand('%'), 'file')
  if new_name != '' && new_name != old_name
    exec ':saveas ' . new_name
    exec ':silent !rm ' . old_name
    redraw!
  endif
endfunction
map <leader>n :call RenameFile()<cr>

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" CUSTOM AUTOCMDS
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
augroup vimrcEx
  " Clear all autocmds in the group
  autocmd!
  " Jump to last cursor position unless it's invalid or in an event handler
  autocmd BufReadPost *
    \ if line("'\"") > 0 && line("'\"") <= line("$") |
    \   exe "normal g`\"" |
    \ endif

  " Leave the return key alone when in command line windows, since it's used
  " to run commands there.
  autocmd! CmdwinEnter * :unmap <cr>
  autocmd! CmdwinLeave * :call MapCR()

  autocmd FileType gitrebase setlocal nomodeline
  autocmd FileType gitcommit setlocal spell
augroup END

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" Use The Silver Searcher if available, else ack
" http://robots.thoughtbot.com/faster-grepping-in-vim
if executable('ag')
  " Use ag over grep
  set grepprg=ag\ --nogroup\ --nocolor

  " Use ag in CtrlP for listing files. Lightning fast and respects .gitignore
  " let g:ctrlp_user_command = 'ag %s -l --nocolor -g ""'
else
  " it's better than grep
  set grepprg=ack
endif

" bind K to grep word under cursor
nnoremap K :grep! "\b<C-R><C-W>\b"<CR>:cw<CR>

" whitespace cleanup - largely "yanked" from:
" http://technotales.wordpress.com/2010/03/31/preserve-a-vim-function-that-keeps-your-state/
function! Preserve(command)
  " Preparation: save last search, and cursor position.
  let _s=@/
  let pos = getpos('.')
  execute a:command
  " Clean up: restore previous search history, and cursor position
  let @/=_s
  call setpos('.', pos)
endfunction

nmap <Leader>w :retab \| :call Preserve('%s/\s\+$//e')<CR>

" tab cycling
map <C-J> :tabprevious<CR>
map <C-K> :tabnext<CR>

" make the current split the only one and turn diff off
nmap <Leader>do :only! \| :diffoff!<CR>

" jslint script
nmap <Leader>j :!jslint %<CR>

" preview in Marked
:nnoremap <leader>m :silent !open -a 'Marked 2' '%:p'<cr>

" vim-test mappings
nnoremap <leader>t :w!\|:TestFile<CR>
nnoremap <leader>s :w!\|:TestNearest<CR>
nnoremap <leader>l :w!\|:TestLast<CR>
nnoremap <leader>a :w!\|:TestSuite<CR>

" Generate tags for current project
map <Leader>c :silent !ctags -R .<CR>

" Run current script
map ,r :w!\|:!%<cr>
