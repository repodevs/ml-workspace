ARG WORKSPACE_VERSION="latest"
# Build from full flavor of workspace with same version
FROM mltooling/ml-workspace:$WORKSPACE_VERSION

ARG WORKSPACE_FLAVOR="gpu"
ENV WORKSPACE_FLAVOR=$WORKSPACE_FLAVOR

USER root

### NVIDIA CUDA BASE ###
# https://gitlab.com/nvidia/cuda/blob/ubuntu16.04/10.0/base/Dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates apt-transport-https gnupg-curl && \
    rm -rf /var/lib/apt/lists/* && \
    NVIDIA_GPGKEY_SUM=d1be581509378368edeec8c1eb2958702feedf3bc3d17011adbf24efacce4ab5 && \
    NVIDIA_GPGKEY_FPR=ae09fe4bbd223a84b2ccfce3f60f4b3d7fa2af80 && \
    apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub && \
    apt-key adv --export --no-emit-version -a $NVIDIA_GPGKEY_FPR | tail -n +5 > cudasign.pub && \
    echo "$NVIDIA_GPGKEY_SUM  cudasign.pub" | sha256sum -c --strict - && rm cudasign.pub && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64 /" > /etc/apt/sources.list.d/cuda.list && \
    echo "deb https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64 /" > /etc/apt/sources.list.d/nvidia-ml.list && \
    # Cleanup - cannot use cleanup script here, otherwise too much is removed
    apt-get clean && \ 
    rm -rf /root/.cache/* && \
    rm -rf /tmp/* && \
    rm -rf /var/lib/apt/lists/*

ENV CUDA_VERSION 10.0.130
ENV CUDA_PKG_VERSION 10-0=$CUDA_VERSION-1

# For libraries in the cuda-compat-* package: https://docs.nvidia.com/cuda/eula/index.html#attachment-a
RUN apt-get update && apt-get install -y --no-install-recommends \
        cuda-cudart-$CUDA_PKG_VERSION \
        cuda-compat-10-0 && \
    ln -s cuda-10.0 /usr/local/cuda && \
    rm -rf /var/lib/apt/lists/* && \
    # Cleanup - cannot use cleanup script here, otherwise too much is removed
    apt-get clean && \ 
    rm -rf /root/.cache/* && \
    rm -rf /tmp/* && \
    rm -rf /var/lib/apt/lists/*


RUN echo "/usr/local/nvidia/lib" >> /etc/ld.so.conf.d/nvidia.conf && \
    echo "/usr/local/nvidia/lib64" >> /etc/ld.so.conf.d/nvidia.conf

ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH}

# nvidia-container-runtime
# https://github.com/NVIDIA/nvidia-container-runtime#environment-variables-oci-spec
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV NVIDIA_REQUIRE_CUDA "cuda>=10.0 brand=tesla,driver>=384,driver<385 brand=tesla,driver>=410,driver<411"

### CUDA RUNTIME ###
# https://gitlab.com/nvidia/cuda/blob/ubuntu16.04/10.0/runtime/Dockerfile

ENV NCCL_VERSION 2.4.2

RUN apt-get update && apt-get install -y --no-install-recommends \
        cuda-libraries-$CUDA_PKG_VERSION \
        cuda-nvtx-$CUDA_PKG_VERSION \
        libnccl2=$NCCL_VERSION-1+cuda10.0 && \
    apt-mark hold libnccl2 && \
    rm -rf /var/lib/apt/lists/* && \
    # Cleanup - cannot use cleanup script here, otherwise too much is removed
    apt-get clean && \ 
    rm -rf /root/.cache/* && \
    rm -rf /tmp/* && \
    rm -rf /var/lib/apt/lists/*

### END CUDA RUNTIME ###

### CUDA DEVEL ###
# https://gitlab.com/nvidia/cuda/blob/ubuntu16.04/10.0/devel/Dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
        cuda-libraries-dev-$CUDA_PKG_VERSION \
        cuda-nvml-dev-$CUDA_PKG_VERSION \
        cuda-minimal-build-$CUDA_PKG_VERSION \
        cuda-command-line-tools-$CUDA_PKG_VERSION \
        libnccl-dev=$NCCL_VERSION-1+cuda10.0 && \
    rm -rf /var/lib/apt/lists/* && \ 
    # Cleanup - cannot use cleanup script here, otherwise too much is removed
    apt-get clean && \ 
    rm -rf /root/.cache/* && \
    rm -rf /tmp/* && \
    rm -rf /var/lib/apt/lists/*

ENV LIBRARY_PATH /usr/local/cuda/lib64/stubs

### END CUDA DEVEL ###

### CUDANN7 DEVEL ###
# https://gitlab.com/nvidia/cuda/blob/ubuntu16.04/10.0/devel/cudnn7/Dockerfile

ENV CUDNN_VERSION 7.6.0.64
LABEL com.nvidia.cudnn.version="${CUDNN_VERSION}"

RUN apt-get update && apt-get install -y --no-install-recommends \
            libcudnn7=$CUDNN_VERSION-1+cuda10.0 \
            libcudnn7-dev=$CUDNN_VERSION-1+cuda10.0 && \
    apt-mark hold libcudnn7 && \
    rm -rf /var/lib/apt/lists/* && \ 
    # Cleanup
    clean-layer.sh

### END CUDANN7 ###

### GPU DATA SCIENCE LIBRARIES ###

RUN \
    apt-get update && apt-get install -y libomp-dev libopenblas-base && \
    # Install cuda-toolkit (e.g. for pytorch: https://pytorch.org/): https://anaconda.org/anaconda/cudatoolkit
    conda install cudatoolkit=10.0 -c pytorch --yes && \
    # Install cupy: https://cupy.chainer.org/
    pip install --no-cache-dir cupy-cuda100 && \
    # Install pycuda: https://pypi.org/project/pycuda
    pip install --no-cache-dir pycuda && \
    # Install gpu utils libs
    pip install --no-cache-dir gpustat py3nvml gputil && \
    # Install scikit-cuda: https://scikit-cuda.readthedocs.io/en/latest/install.html
    pip install --no-cache-dir scikit-cuda && \
    # Install tensorflow gpu - conda uninstall removes too much and conda remove corrupts environment
    pip uninstall -y tensorflow && \
    pip install --no-cache-dir tensorflow-gpu && \
    # Install ONNX GPU Runtime
    pip uninstall -y onnxruntime && \
    pip install --no-cache-dir onnxruntime-gpu==0.4.0 && \
    # Install cntk
    pip uninstall -y cntk && \
    pip install --no-cache-dir cntk-gpu && \
    # Install pytorch gpu - conda uninstall removes too much and conda remove corrupts environment
    pip uninstall -y pytorch-cpu torchvision-cpu && \
    conda install -y pytorch torchvision cudatoolkit=10.0 -c pytorch --yes && \
    # install jax: https://github.com/google/jax#pip-installation
    pip install --no-cache-dir --upgrade https://storage.googleapis.com/jax-wheels/cuda100/jaxlib-0.1.21-cp36-none-linux_x86_64.whl && \
    pip install --no-cache-dir --upgrade jax  && \
    # Install Rapids: https://rapids.ai/start.html#conda-install
    conda install -y -c defaults -c nvidia -c rapidsai -c pytorch -c numba -c conda-forge \
            cudf=0.7 \
            cuml=0.7 \
            cugraph=0.7 \
            nvstrings=0.7 \
            dask-cuda=0.7 \ 
            dask-cudf=0.7 \
            dask-cuml=0.7 && \
    # Install pygpu - Required for theano: http://deeplearning.net/software/libgpuarray/
    conda install -y pygpu && \
    # Install Spacy GPU Support:
    pip install --no-cache-dir thinc-gpu-ops && \
    # MXNet with GPU Support:
    # pip install --no-cache-dir --upgrade mxnet-cu100 && \
    # Cleanup
    clean-layer.sh

# https://www.anaconda.com/getting-started-with-gpu-computing-in-anaconda/

# By default, the majority of GPU memory will be allocated by the first
# execution of a TensorFlow graph. While this behavior can be desirable for
# production pipelines, it is less desirable for interactive use. Set
# TF_FORCE_GPU_ALLOW_GROWTH to change this default behavior as if the user had
ENV TF_FORCE_GPU_ALLOW_GROWTH true

### END DATA SCIENCE LIBRARIES ###

### GPU TOOLS ###

# Install Glances & Netdata GPU Support
RUN \
    pip install --upgrade --force-reinstall nvidia-ml-py3 && \ 
    apt-get update -y && \
    apt-get install lm-sensors -y && \
    apt-get install netcat -y && \
    apt-get install iproute -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    git clone https://github.com/Splo0sh/netdata_nv_plugin --depth 1 /tmp/netdata_nv_plugin && \
    cp /tmp/netdata_nv_plugin/nv.chart.py /usr/libexec/netdata/python.d/ && \
    cp /tmp/netdata_nv_plugin/python_modules/pynvml.py /usr/libexec/netdata/python.d/python_modules/ && \
    cp /tmp/netdata_nv_plugin/nv.conf /etc/netdata/python.d/ && \
    # Cleanup
    clean-layer.sh

### END GPU TOOLS ###

### CONFIGURATION ###

RUN \
    echo 'Defaults env_keep += "ftp_proxy http_proxy https_proxy no_proxy"' >> /etc/sudoers

# Overwrite & add Labels
LABEL \
    "workspace.flavor"=$WORKSPACE_FLAVOR

# TODO use temp as data environment to use temp folder?
# DATA_ENVIRONMENT="temp"

# USER $NB_USER

#RUN \
#    echo "export PATH=$PATH" >> $HOME/.bashrc
