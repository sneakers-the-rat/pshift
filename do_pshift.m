shift = 6;

in_dir = '/home/lab/speech_recordings/raw/';
out_dir = '/home/lab/speech_recordings/pshift/';


files = getFilenames(in_dir);
n_files = length(files);

% Set pitch shift params - this is largely the same as the original
% parameters from "Improving Time-Scale Modification of Music
% Signals using Harmonic-Percussive Separation" by Driedger and Mueller.
% with some empirical modifications
params = struct();

params.hpsWin = win(2^12,2);
params.hpsAnaHop = 2^10;
params.hpsFilLenHarm = 11;
params.hpsFilLenPerc = 11;
params.pvWin = win(2^13,2);
params.pvSynHop = 2^12;
%params.pvSynHop = 4096;
%params.pvWin    = win(params.pvSynHop*2, 2);
params.olaSynHop = 2^7;
params.olaWin = win(2^11, 2);
params.pvFftShift = 1;
params.pvRestoreEnergy = 1;

wb = waitbar(0, '', 'Name', 'Processing Files');

for i = 2:n_files
    file = files{i};
    fn = strrep(file, in_dir, '');
    save_fn = strrep(file, in_dir, out_dir);
    waitbar(i/n_files, wb, sprintf('Processing: %s',fn));
    
    % load audio, do pitch shifting, return to original sampling rate
    [audio, fs] = audioread(file);
    [audio, info] = hpTSM(audio, shift, params);
    audio = resample(audio, fs,fs*shift, 8);
    
    audiowrite(save_fn, audio, fs, 'BitsPerSample', 32);
    
    
end