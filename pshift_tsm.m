% pitch shift with the TSM toolbox
% https://www.audiolabs-erlangen.de/resources/MIR/TSMtoolbox/
% [DM14] Jonathan Driedger, Meinard Mueller
%        TSM Toolbox: MATLAB Implementations of Time-Scale Modification 
%        Algorithms
%        Proceedings of the 17th International Conference on Digital Audio  
%        Effects, Erlangen, Germany, 2014.

function compare_methods(shift)
    %shift = 6;

    fn = '/home/lab/speech_recordings/Aldis/Aldis_cv_1.wav';
    [audio, fs] = audioread(fn);

    % subset 5s
    audio_s = audio(1:fs*5,1);

    spectrogram(audio_s, 2048, 512, 4096, fs, 'yaxis')
    ylim([0,20])
    colormap('bone')

    %% Elastique
    params = struct();
    params.fsAudio = fs;

    if shift>4
        [audio_el, info] = elastiqueTSM(audio_s, 4, params);
        audio_el = resample(audio_el, fs,fs*4, 8);
        eshift = shift-4;
        while eshift>4
            [audio_el, info] = elastiqueTSM(audio_el, 2, params);
            audio_el = resample(audio_el, fs,fs*2, 8);
            eshift = eshift-4;
        end
        [audio_el, info] = elastiqueTSM(audio_el, eshift, params);
        audio_el = resample(audio_el, fs,fs*eshift, 8);
    else
        [audio_el, info] = elastiqueTSM(audio_s, shift, params);
        audio_el = resample(audio_el, fs,fs*shift, 8);
    end



    %% hpTSM
    params = struct();

    params.hpsWin = win(1024,2);
    params.hpsAnaHop = 512;
    params.hpsFilLenHarm = 21;
    params.hpsFilLenPerc = 21;
    params.pvWin = win(8192,2);
    params.pvSynHop = 4096;
    %params.pvSynHop = 4096;
    %params.pvWin    = win(params.pvSynHop*2, 2);
    params.olaSynHop = 2048;
    params.olaWin = win(params.olaSynHop*2, 2);
    params.pvFftShift = 1;
    params.pvRestoreEnergy = 1;
    
    
    [audio_hp, info] = hpTSM(audio_s, shift, params);
    
    audio_hp = resample(audio_hp, fs,fs*shift, 8);
    audiowrite('test_hp_slo.wav', audio_hp, fs, 'BitsPerSample',32)
    
    
    
    %% 





    figure;
    subplot(3,1,1)
    spectrogram(audio_dn, 2048, 512,2^14, fs, 'yaxis')
    ylim([0,8])
    colormap('bone')

    subplot(3,1,2)
    spectrogram(audio_el, 2048/shift, 512/shift, 2^14, fs, 'yaxis')
    ylim([0,8*shift])
    colormap('bone')
    
    subplot(3,1,3)
    spectrogram(audio_hp, 2048/shift, 512/shift, 2^14, fs, 'yaxis')
    ylim([0,8*shift])
    colormap('bone')

end

function shift(method, shift)


end