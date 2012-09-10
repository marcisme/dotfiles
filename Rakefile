
desc 'install dot files'
task :install do
  Dir.glob('**/*.ln').each do |file|
    source_file = File.join(Dir.pwd, file)
    link_file = File.join(ENV['HOME'], '.' + File.basename(file).sub('.ln', ''))
    backup_file = link_file + '.backup'

    if File.exists?(link_file) && !File.symlink?(link_file)
      puts "backing up #{link_file} to #{backup_file}"
      FileUtils.mv(link_file, backup_file)
    end

    # remove existing link, so we don't get a link in a directory
    if File.symlink?(link_file)
      puts "removing existing link"
      FileUtils.rm(link_file)
    end

    puts "Linking #{link_file} to #{source_file}"
    FileUtils.ln_sf(source_file, link_file)
  end
end

task :default => :install

