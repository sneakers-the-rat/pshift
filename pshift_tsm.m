% pitch shift with the TSM toolbox
% https://www.audiolabs-erlangen.de/resources/MIR/TSMtoolbox/
% [DM14] Jonathan Driedger, Meinard Mueller
%        TSM Toolbox: MATLAB Implementations of Time-Scale Modification 
%        Algorithms
%        Proceedings of the 17th International Conference on Digital Audio  
%        Effects, Erlangen, Germany, 2014.

function compare_methods(shift)
    shift = 6;

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




    
    
    
    %% 





    figure;
    subplot(2,1,1)
    spectrogram(audio(fs*10:fs*50), 2048, 512,2^14, fs, 'yaxis')
    ylim([0,8])
    colormap('bone')

%     subplot(3,1,2)
%     spectrogram(audio_el, 2048/shift, 512/shift, 2^14, fs, 'yaxis')
%     ylim([0,8*shift])
%     colormap('bone')
    
    subplot(2,1,2)
    spectrogram(audio_hp(fs*10:fs*50), 2048, 512, 2^14, fs, 'yaxis')
    ylim([0,8])
    colormap('bone')

end



function shift(method, shift)


end