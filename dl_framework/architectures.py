from torch import nn
import torch
from dl_framework.model import (
    conv,
    Lambda,
    flatten,
    fft,
    deconv,
    double_conv,
    cut_off,
    flatten_with_channel,
    depth_conv,
    LocallyConnected2d,
    symmetry,
    shape,
    phase_range,
    GeneralELU,
    conv_phase,
    conv_amp,
)
from functools import partial
from math import pi


def cnn():
    """
    conv-layer: number of entry channels, number of exit channels,
                kerner size, stride, padding
    """
    arch = nn.Sequential(
        *conv(2, 4, (3, 3), 2, 1),
        *conv(4, 8, (3, 3), 2, 1),
        *conv(8, 16, (3, 3), 2, 1),
        nn.MaxPool2d((3, 3)),
        *conv(16, 32, (2, 2), 2, 1),
        *conv(32, 64, (2, 2), 2, 1),
        nn.MaxPool2d((2, 2)),
        Lambda(flatten),
        nn.Linear(64, 8192),
        Lambda(fft),
        Lambda(flatten),
        # *conv(2, 1, 1, 1, 0),
        nn.Linear(8192, 4096),
        # Lambda(flatten),
    )
    return arch


def small():
    """
    conv-layer: number of entry channels, number of exit channels,
                kerner size, stride, padding
    """
    arch = nn.Sequential(
        Lambda(flatten), Lambda(fft), Lambda(flatten), nn.Linear(8192, 4096),
    )
    return arch


def autoencoder():
    arch = nn.Sequential(
        *conv(2, 4, (3, 3), 2, 1),
        *conv(4, 8, (3, 3), 2, 1),
        *conv(8, 16, (3, 3), 2, 1),
        nn.MaxPool2d((3, 3)),
        *conv(16, 32, (2, 2), 2, 1),
        *conv(32, 64, (2, 2), 2, 1),
        nn.MaxPool2d((2, 2)),
        *deconv(64, 32, (3, 3), 2, 1, 0),
        *deconv(32, 16, (3, 3), 2, 1, 0),
        *deconv(16, 16, (3, 3), 2, 1, 0),
        *deconv(16, 8, (3, 3), 2, 1, 0),
        *deconv(8, 4, (3, 3), 2, 1, 0),
        # nn.ConvTranspose2d(4, 2, (3, 3), 2, 1, 1),
        *deconv(4, 2, (3, 3), 2, 1, 0),
        Lambda(flatten),
        # nn.Linear(8192, 4096)
        nn.Linear(2, 4096),
    )
    return arch


class UNet_fft(nn.Module):
    def __init__(self):
        super().__init__()

        self.dconv_down1 = nn.Sequential(*double_conv(2, 4, (3, 3), 1, 1),)
        self.dconv_down2 = nn.Sequential(*double_conv(4, 8, (3, 3), 1, 1),)
        self.dconv_down3 = nn.Sequential(*double_conv(8, 16, (3, 3), 1, 1),)
        self.dconv_down4 = nn.Sequential(*double_conv(16, 32, (3, 3), 1, 1),)
        self.dconv_down5 = nn.Sequential(*double_conv(32, 64, (3, 3), 1, 1),)

        self.maxpool = nn.MaxPool2d(2)
        self.upsample1 = nn.Upsample(size=7, mode="bilinear", align_corners=True)
        self.upsample2 = nn.Upsample(size=15, mode="bilinear", align_corners=True)
        self.upsample3 = nn.Upsample(size=31, mode="bilinear", align_corners=True)
        self.upsample4 = nn.Upsample(size=63, mode="bilinear", align_corners=True)

        self.dconv_up4 = nn.Sequential(*double_conv(32 + 64, 32, (3, 3), 1, 1),)
        self.dconv_up3 = nn.Sequential(*double_conv(16 + 32, 16, (3, 3), 1, 1),)
        self.dconv_up2 = nn.Sequential(*double_conv(8 + 16, 8, (3, 3), 1, 1),)
        self.dconv_up1 = nn.Sequential(*double_conv(4 + 8, 4, (3, 3), 1, 1),)

        self.conv_last = nn.Conv2d(4, 2, 1)
        self.flatten = Lambda(flatten)
        self.linear1 = nn.Linear(8192, 4096)
        self.fft = Lambda(fft)

    def forward(self, x):
        conv1 = self.dconv_down1(x)
        x = self.maxpool(conv1)
        conv2 = self.dconv_down2(x)
        x = self.maxpool(conv2)
        conv3 = self.dconv_down3(x)
        x = self.maxpool(conv3)
        conv4 = self.dconv_down4(x)
        x = self.maxpool(conv4)
        x = self.dconv_down5(x)

        x = self.upsample1(x)
        x = torch.cat([x, conv4], dim=1)
        x = self.dconv_up4(x)
        x = self.upsample2(x)
        x = torch.cat([x, conv3], dim=1)
        x = self.dconv_up3(x)
        x = self.upsample3(x)
        x = torch.cat([x, conv2], dim=1)
        x = self.dconv_up2(x)
        x = self.upsample4(x)
        x = torch.cat([x, conv1], dim=1)
        x = self.dconv_up1(x)
        x = self.conv_last(x)

        x = self.flatten(x)
        x = self.fft(x)
        x = self.flatten(x)
        out = self.linear1(x)

        return out


class UNet_denoise(nn.Module):
    def __init__(self):
        super().__init__()

        self.dconv_down1 = nn.Sequential(*double_conv(2, 4, (3, 3), 1, 1),)
        self.dconv_down2 = nn.Sequential(*double_conv(4, 8, (3, 3), 1, 1),)
        self.dconv_down3 = nn.Sequential(*double_conv(8, 16, (3, 3), 1, 1),)
        self.dconv_down4 = nn.Sequential(*double_conv(16, 32, (3, 3), 1, 1),)
        self.dconv_down5 = nn.Sequential(*double_conv(32, 64, (3, 3), 1, 1),)

        self.maxpool = nn.MaxPool2d(2)
        self.upsample1 = nn.Upsample(size=7, mode="bilinear", align_corners=True)
        self.upsample2 = nn.Upsample(size=15, mode="bilinear", align_corners=True)
        self.upsample3 = nn.Upsample(size=31, mode="bilinear", align_corners=True)
        self.upsample4 = nn.Upsample(size=63, mode="bilinear", align_corners=True)

        self.dconv_up4 = nn.Sequential(*double_conv(32 + 64, 32, (3, 3), 1, 1),)
        self.dconv_up3 = nn.Sequential(*double_conv(16 + 32, 16, (3, 3), 1, 1),)
        self.dconv_up2 = nn.Sequential(*double_conv(8 + 16, 8, (3, 3), 1, 1),)
        self.dconv_up1 = nn.Sequential(*double_conv(4 + 8, 4, (3, 3), 1, 1),)

        self.conv_last = nn.Conv2d(4, 2, 1)
        self.flatten = Lambda(flatten)
        self.linear = nn.Linear(7938, 3969)
        self.fft = Lambda(fft)
        self.cut = Lambda(cut_off)
        self.shape = Lambda(shape)

    def forward(self, x):
        x = self.flatten(x)
        x = self.fft(x)
        conv1 = self.dconv_down1(x)
        x = self.maxpool(conv1)
        conv2 = self.dconv_down2(x)
        x = self.maxpool(conv2)
        conv3 = self.dconv_down3(x)
        x = self.maxpool(conv3)
        conv4 = self.dconv_down4(x)
        x = self.maxpool(conv4)
        x = self.dconv_down5(x)

        x = self.upsample1(x)
        x = torch.cat([x, conv4], dim=1)
        x = self.dconv_up4(x)
        x = self.upsample2(x)
        x = torch.cat([x, conv3], dim=1)
        x = self.dconv_up3(x)
        x = self.upsample3(x)
        x = torch.cat([x, conv2], dim=1)
        x = self.dconv_up2(x)
        x = self.upsample4(x)
        x = torch.cat([x, conv1], dim=1)
        x = self.dconv_up1(x)
        x = self.conv_last(x)
        x = self.flatten(x)
        out = self.linear(x)

        return out


class UNet_fourier(nn.Module):
    def __init__(self):
        super().__init__()

        self.dconv_down1 = nn.Sequential(*double_conv(2, 4, (3, 3), 1, 1),)
        self.dconv_down2 = nn.Sequential(*double_conv(4, 8, (3, 3), 1, 1),)
        self.dconv_down3 = nn.Sequential(*double_conv(8, 16, (3, 3), 1, 1),)
        self.dconv_down4 = nn.Sequential(*double_conv(16, 32, (3, 3), 1, 1),)
        self.dconv_down5 = nn.Sequential(*double_conv(32, 64, (3, 3), 1, 1),)

        self.maxpool = nn.MaxPool2d(2)
        self.upsample1 = nn.Upsample(size=7, mode="bilinear", align_corners=True)
        self.upsample2 = nn.Upsample(size=15, mode="bilinear", align_corners=True)
        self.upsample3 = nn.Upsample(size=31, mode="bilinear", align_corners=True)
        self.upsample4 = nn.Upsample(size=63, mode="bilinear", align_corners=True)

        self.dconv_up4 = nn.Sequential(*double_conv(32 + 64, 32, (3, 3), 1, 1),)
        self.dconv_up3 = nn.Sequential(*double_conv(16 + 32, 16, (3, 3), 1, 1),)
        self.dconv_up2 = nn.Sequential(*double_conv(8 + 16, 8, (3, 3), 1, 1),)
        self.dconv_up1 = nn.Sequential(*double_conv(4 + 8, 4, (3, 3), 1, 1),)

        self.conv_last = nn.Conv2d(4, 2, 1)
        self.linear = nn.Linear(8192, 4096)
        self.flatten = Lambda(flatten)
        self.flatten_with_channel = Lambda(flatten_with_channel)

    def forward(self, x):
        conv1 = self.dconv_down1(x)
        x = self.maxpool(conv1)
        conv2 = self.dconv_down2(x)
        x = self.maxpool(conv2)
        conv3 = self.dconv_down3(x)
        x = self.maxpool(conv3)
        conv4 = self.dconv_down4(x)
        x = self.maxpool(conv4)
        x = self.dconv_down5(x)

        x = self.upsample1(x)
        x = torch.cat([x, conv4], dim=1)
        x = self.dconv_up4(x)
        x = self.upsample2(x)
        x = torch.cat([x, conv3], dim=1)
        x = self.dconv_up3(x)
        x = self.upsample3(x)
        x = torch.cat([x, conv2], dim=1)
        x = self.dconv_up2(x)
        x = self.upsample4(x)
        x = torch.cat([x, conv1], dim=1)
        x = self.dconv_up1(x)
        x = self.conv_last(x)
        # out = self.flatten_with_channel(x)

        return x


class UNet_denoise_64(nn.Module):
    def __init__(self):
        super().__init__()
        self.dconv_down1 = nn.Sequential(*double_conv(2, 4, (3, 3), 1, 1),)
        self.dconv_down2 = nn.Sequential(*double_conv(4, 8, (3, 3), 1, 1),)
        self.dconv_down3 = nn.Sequential(*double_conv(8, 16, (3, 3), 1, 1),)
        self.dconv_down4 = nn.Sequential(*double_conv(16, 32, (3, 3), 1, 1),)
        self.dconv_down5 = nn.Sequential(*double_conv(32, 64, (3, 3), 1, 1),)
        self.maxpool = nn.MaxPool2d(2)
        self.upsample = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True)
        self.dconv_up4 = nn.Sequential(*double_conv(32 + 64, 32, (3, 3), 1, 1),)
        self.dconv_up3 = nn.Sequential(*double_conv(16 + 32, 16, (3, 3), 1, 1),)
        self.dconv_up2 = nn.Sequential(*double_conv(8 + 16, 8, (3, 3), 1, 1),)
        self.dconv_up1 = nn.Sequential(*double_conv(4 + 8, 4, (3, 3), 1, 1),)
        self.conv_last = nn.Conv2d(4, 2, 1)
        self.flatten = Lambda(flatten)
        self.linear = nn.Linear(8192, 4096)
        self.fft = Lambda(fft)
        self.cut = Lambda(cut_off)

    def forward(self, x):
        x = self.flatten(x)
        x = self.fft(x)
        conv1 = self.dconv_down1(x)
        x = self.maxpool(conv1)
        conv2 = self.dconv_down2(x)
        x = self.maxpool(conv2)
        conv3 = self.dconv_down3(x)
        x = self.maxpool(conv3)
        conv4 = self.dconv_down4(x)
        x = self.maxpool(conv4)
        x = self.dconv_down5(x)
        x = self.upsample(x)
        x = torch.cat([x, conv4], dim=1)
        x = self.dconv_up4(x)
        x = self.upsample(x)
        x = torch.cat([x, conv3], dim=1)
        x = self.dconv_up3(x)
        x = self.upsample(x)
        x = torch.cat([x, conv2], dim=1)
        x = self.dconv_up2(x)
        x = self.upsample(x)
        x = torch.cat([x, conv1], dim=1)
        x = self.dconv_up1(x)
        x = self.conv_last(x)
        x = self.flatten(x)
        out = self.linear(x)
        return out


def convs():
    arch = nn.Sequential(
        Lambda(flatten),
        Lambda(fft),
        *conv(2, 4, (3, 3), 2, 1),
        *conv(4, 8, (3, 3), 2, 1),
        *conv(8, 16, (3, 3), 2, 1),
        Lambda(flatten),
        nn.Linear(1024, 1024),
        Lambda(flatten_with_channel),
        nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
        *conv(16, 8, (3, 3), 1, 1),
        nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
        *conv(8, 4, (3, 3), 1, 1),
        nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
        *conv(4, 1, (3, 3), 1, 1),
        Lambda(flatten),
    )
    return arch


class conv_filter(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Sequential(*conv(2, 1, (5, 5), 1, 2))
        self.conv2 = nn.Sequential(*conv(1, 128, (5, 5), 1, 2))
        self.conv3 = nn.Sequential(*conv(128, 1, (5, 5), 1, 2))
        self.flatten = Lambda(flatten)

    def forward(self, x):
        x = self.conv1(x)
        inp = x.clone()
        x = self.conv2(x)
        x = self.conv3(x)
        out = x + inp
        out = self.flatten(out)

        return out


class depthwise_seperable_conv(nn.Module):
    def __init__(self):
        super().__init__()

        self.depth1 = nn.Sequential(
            *depth_conv(1, 64, (7, 7), stride=1, padding=6, dilation=2)
        )
        self.depth12 = nn.Sequential(
            *depth_conv(1, 64, (7, 7), stride=1, padding=3, dilation=1)
        )
        self.depth2 = nn.Sequential(
            *depth_conv(1, 64, (7, 7), stride=1, padding=6, dilation=2)
        )
        self.depth21 = nn.Sequential(
            *depth_conv(1, 64, (7, 7), stride=1, padding=3, dilation=1)
        )
        self.point1 = nn.Sequential(*conv(128, 1, (1, 1), 1, 0))
        self.point2 = nn.Sequential(*conv(128, 1, (1, 1), 1, 0))
        self.flatten = Lambda(flatten_with_channel)

    def forward(self, x):
        # inp = x.clone()
        inp_real = x[:, 0, :].view(x.shape[0], 1, x.shape[2], x.shape[3])
        inp_imag = x[:, 1, :].view(x.shape[0], 1, x.shape[2], x.shape[3])

        depth1 = self.depth1(inp_real)
        depth12 = self.depth12(inp_real)

        depth2 = self.depth2(inp_imag)
        depth21 = self.depth21(inp_imag)

        comb1 = torch.cat([depth1, depth12], dim=1)
        comb2 = torch.cat([depth2, depth21], dim=1)

        point1 = self.point1(comb1)
        point2 = self.point2(comb2)

        comb = torch.cat([point1, point2], dim=1)
        # comb = comb + inp
        out = self.flatten(comb)

        return comb


class small_fourier(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv_last = nn.Conv2d(4, 2, 1)
        self.flatten_with_channel = Lambda(flatten_with_channel)
        self.conv1 = nn.Sequential(*conv(2, 4, (3, 3), stride=1, padding=1))

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv_last(x)
        out = self.flatten_with_channel(x)

        return out


class filter(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=32,
                kernel_size=(3, 3),
                stride=1,
                padding=1,
                dilation=1,
                padding_mode="zeros",
                bias=False,
            ),
            nn.BatchNorm2d(32),
            nn.ELU(),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=32,
                kernel_size=(3, 3),
                stride=1,
                padding=2,
                dilation=2,
                padding_mode="zeros",
                bias=False,
            ),
            nn.BatchNorm2d(32),
            nn.ELU(),
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=32,
                kernel_size=(5, 5),
                stride=1,
                padding=2,
                dilation=1,
                padding_mode="zeros",
                bias=False,
            ),
            nn.BatchNorm2d(32),
            nn.ELU(),
        )
        self.conv4 = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=32,
                kernel_size=(5, 5),
                stride=1,
                padding=4,
                dilation=2,
                padding_mode="zeros",
                bias=False,
            ),
            nn.BatchNorm2d(32),
            nn.ELU(),
        )
        self.conv5 = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=32,
                kernel_size=(7, 7),
                stride=1,
                padding=3,
                dilation=1,
                padding_mode="zeros",
                bias=False,
            ),
            nn.BatchNorm2d(32),
            nn.ELU(),
        )
        self.conv6 = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=32,
                kernel_size=(9, 9),
                stride=1,
                padding=4,
                dilation=1,
                padding_mode="zeros",
                bias=False,
            ),
            nn.BatchNorm2d(32),
            nn.ELU(),
        )
        self.conv_last = nn.Sequential(
            LocallyConnected2d(192, 2, 63, 1, stride=1, bias=False),
            nn.BatchNorm2d(2),
            nn.ELU(),
        )
        self.elu = nn.ELU()
        self.symmetry = Lambda(symmetry)

    def forward(self, x):
        inp = x.clone()
        comb = torch.cat(
            [
                self.conv1(x),
                self.conv2(x),
                self.conv3(x),
                self.conv4(x),
                self.conv5(x),
                self.conv6(x),
            ],
            dim=1,
        )
        x = self.conv_last(comb)
        x = x.clone()
        x[:, 0][inp[:, 0] != 0] = inp[:, 0][inp[:, 0] != 0]
        #  x[:, 0][inp[:, 0] == 0] += 1
        x0 = self.symmetry(x[:, 0]).reshape(-1, 1, 63, 63)
        x[:, 1][inp[:, 0] == 0] += 1e-5 + 1
        x[:, 1][inp[:, 0] != 0] = 1e-8
        x = self.elu(x)
        x1 = self.symmetry(x[:, 1]).reshape(-1, 1, 63, 63)
        out = torch.cat([x0, x1], dim=1)
        return out


class filter_deep(nn.Module):
    def __init__(self, img_size):
        super().__init__()
        self.conv1_amp = nn.Sequential(
            *conv_amp(1, 4, (23, 23), 1, 11, 1)
        )
        self.conv1_phase = nn.Sequential(
            *conv_phase(1, 4, (23, 23), 1, 11, 1, add=1-pi)
        )
        self.conv2_amp = nn.Sequential(
             *conv_amp(4, 8, (21, 21), 1, 10, 1)
        )
        self.conv2_phase = nn.Sequential(
             *conv_phase(4, 8, (21, 21), 1, 10, 1, add=1-pi)
        )
        self.conv3_amp = nn.Sequential(
             *conv_amp(8, 12, (17, 17), 1, 8, 1)
        )
        self.conv3_phase = nn.Sequential(
             *conv_phase(8, 12, (17, 17), 1, 8, 1, add=1-pi)
        )
        self.conv_con1_amp = nn.Sequential(
            LocallyConnected2d(12, 1, img_size, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            nn.ReLU(),
        )
        self.conv_con1_phase = nn.Sequential(
            LocallyConnected2d(12, 1, img_size, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            GeneralELU(1-pi),
        )

        self.conv4_amp = nn.Sequential(
             *conv_amp(1, 4, (5, 5), 1, 3, 2)
        )
        self.conv4_phase = nn.Sequential(
             *conv_phase(1, 4, (5, 5), 1, 3, 2, add=1-pi)
        )
        self.conv5_amp = nn.Sequential(
             *conv_amp(4, 8, (5, 5), 1, 2, 1)
        )
        self.conv5_phase = nn.Sequential(
             *conv_phase(4, 8, (5, 5), 1, 2, 1, add=1-pi)
        )
        self.conv6_amp = nn.Sequential(
             *conv_amp(8, 12, (3, 3), 1, 3, 2)
        )
        self.conv6_phase = nn.Sequential(
             *conv_phase(8, 12, (3, 3), 1, 3, 2, add=1-pi)
        )
        self.conv7_amp = nn.Sequential(
             *conv_amp(12, 16, (3, 3), 1, 1, 1)
        )
        self.conv7_phase = nn.Sequential(
             *conv_phase(12, 16, (3, 3), 1, 1, 1, add=1-pi)
        )
        self.conv_con2_amp = nn.Sequential(
            LocallyConnected2d(16, 1, img_size, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            nn.ReLU(),
        )
        self.conv_con2_phase = nn.Sequential(
            LocallyConnected2d(16, 1, img_size, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            GeneralELU(1-pi),
        )

        self.conv8_amp = nn.Sequential(
             *conv_amp(1, 4, (3, 3), 1, 1, 1)
        )
        self.conv8_phase = nn.Sequential(
             *conv_phase(1, 4, (3, 3), 1, 1, 1, add=1-pi)
        )
        self.conv9_amp = nn.Sequential(
             *conv_amp(4, 8, (3, 3), 1, 1, 1)
        )
        self.conv9_phase = nn.Sequential(
             *conv_phase(4, 8, (3, 3), 1, 1, 1, add=1-pi)
        )
        self.conv10_amp = nn.Sequential(
             *conv_amp(8, 12, (3, 3), 1, 2, 2)
        )
        self.conv10_phase = nn.Sequential(
             *conv_phase(8, 12, (3, 3), 1, 2, 2, add=1-pi)
        )
        self.conv11_amp = nn.Sequential(
             *conv_amp(12, 20, (3, 3), 1, 1, 1)
        )
        self.conv11_phase = nn.Sequential(
             *conv_phase(12, 20, (3, 3), 1, 1, 1, add=1-pi)
        )
        self.conv_con3_amp = nn.Sequential(
            LocallyConnected2d(20, 1, img_size, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            nn.ReLU(),
        )
        self.conv_con3_phase = nn.Sequential(
            LocallyConnected2d(20, 1, img_size, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            GeneralELU(1-pi),
        )
        self.symmetry_real = Lambda(symmetry)
        self.symmetry_imag = Lambda(partial(symmetry, mode='imag'))

    def forward(self, x):
        x = x[:, 0].unsqueeze(1)
        inp = x.clone()
        amp = x[:, 0, :].unsqueeze(1)
        phase = x[:, 1, :].unsqueeze(1)

        amp = self.conv1_amp(amp)
        phase = self.conv1_phase(phase)

        amp = self.conv2_amp(amp)
        phase = self.conv2_phase(phase)

        amp = self.conv3_amp(amp)
        phase = self.conv3_phase(phase)

        amp = self.conv_con1_amp(amp)
        phase = self.conv_con1_phase(phase)

        # Second block
        amp = self.conv4_amp(amp)
        phase = self.conv4_phase(phase)

        amp = self.conv5_amp(amp)
        phase = self.conv5_phase(phase)

        amp = self.conv6_amp(amp)
        phase = self.conv6_phase(phase)

        amp = self.conv7_amp(amp)
        phase = self.conv7_phase(phase)

        amp = self.conv_con2_amp(amp)
        phase = self.conv_con2_phase(phase)

        # Third block
        amp = self.conv8_amp(amp)
        phase = self.conv8_phase(phase)

        amp = self.conv9_amp(amp)
        phase = self.conv9_phase(phase)

        amp = self.conv10_amp(amp)
        phase = self.conv10_phase(phase)

        amp = self.conv11_amp(amp)
        phase = self.conv11_phase(phase)

        amp = self.conv_con3_amp(amp)
        phase = self.conv_con3_phase(phase)

        # amp = amp + inp[:, 0].unsqueeze(1)
        inp_amp = inp[:, 0].unsqueeze(1)
        inp_phase = inp[:, 1].unsqueeze(1)
        # phase = phase + inp[:, 1].unsqueeze(1)
        x0 = self.symmetry_real(amp).reshape(-1, 1, amp.shape[2], amp.shape[2])
        x0[inp_amp != 0] = inp_amp[inp_amp != 0]

        x1 = self.symmetry_imag(phase).reshape(-1, 1, phase.shape[2], phase.shape[2])
        x1[inp_phase != 0] = inp_phase[inp_phase != 0]
        comb = torch.cat([x0, x1], dim=1)
        return comb


class filter_deep_amp(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1_amp = nn.Sequential(
            *conv_amp(1, 4, (23, 23), 1, 11, 1)
        )
        self.conv2_amp = nn.Sequential(
             *conv_amp(4, 8, (21, 21), 1, 10, 1)
        )
        self.conv3_amp = nn.Sequential(
             *conv_amp(8, 12, (17, 17), 1, 8, 1)
        )
        self.conv_con1_amp = nn.Sequential(
            LocallyConnected2d(12, 1, 63, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            nn.ReLU(),
        )

        self.conv4_amp = nn.Sequential(
             *conv_amp(1, 4, (5, 5), 1, 3, 2)
        )
        self.conv5_amp = nn.Sequential(
             *conv_amp(4, 8, (5, 5), 1, 2, 1)
        )
        self.conv6_amp = nn.Sequential(
             *conv_amp(8, 12, (3, 3), 1, 3, 2)
        )
        self.conv7_amp = nn.Sequential(
             *conv_amp(12, 16, (3, 3), 1, 1, 1)
        )
        self.conv_con2_amp = nn.Sequential(
            LocallyConnected2d(16, 1, 63, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            nn.ReLU(),
        )

        self.conv8_amp = nn.Sequential(
             *conv_amp(1, 4, (3, 3), 1, 1, 1)
        )
        self.conv9_amp = nn.Sequential(
             *conv_amp(4, 8, (3, 3), 1, 1, 1)
        )
        self.conv10_amp = nn.Sequential(
             *conv_amp(8, 12, (3, 3), 1, 2, 2)
        )
        self.conv_con3_amp = nn.Sequential(
            LocallyConnected2d(12, 1, 63, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            nn.ReLU(),
        )
        self.symmetry_real = Lambda(symmetry)

    def forward(self, x):
        inp = x.clone()
        amp = x[:, 0, :].unsqueeze(1)

        # First block
        amp = self.conv1_amp(amp)

        amp = self.conv2_amp(amp)

        amp = self.conv3_amp(amp)

        amp = self.conv_con1_amp(amp)

        # Second block
        amp = self.conv4_amp(amp)

        amp = self.conv5_amp(amp)

        amp = self.conv6_amp(amp)

        amp = self.conv7_amp(amp)

        amp = self.conv_con2_amp(amp)

        # Third block
        amp = self.conv8_amp(amp)

        amp = self.conv9_amp(amp)

        amp = self.conv10_amp(amp)

        amp = self.conv_con3_amp(amp)

        amp = amp + inp[:, 0].unsqueeze(1)
        x0 = self.symmetry_real(amp).reshape(-1, 1, 63, 63)
        return x0


class filter_deep_phase(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1_phase = nn.Sequential(
            *conv_phase(1, 4, (23, 23), 1, 11, 1, add=-2.1415)
        )
        self.conv2_phase = nn.Sequential(
             *conv_phase(4, 8, (21, 21), 1, 10, 1, add=-2.1415)
        )
        self.conv3_phase = nn.Sequential(
             *conv_phase(8, 12, (17, 17), 1, 8, 1, add=-2.1415)
        )
        self.conv_con1_phase = nn.Sequential(
            LocallyConnected2d(12, 1, 63, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            GeneralELU(-2.1415),
        )

        self.conv4_phase = nn.Sequential(
             *conv_phase(1, 4, (5, 5), 1, 3, 2, add=-2.1415)
        )
        self.conv5_phase = nn.Sequential(
             *conv_phase(4, 8, (5, 5), 1, 2, 1, add=-2.1415)
        )
        self.conv6_phase = nn.Sequential(
             *conv_phase(8, 12, (3, 3), 1, 3, 2, add=-2.1415)
        )
        self.conv7_phase = nn.Sequential(
             *conv_phase(12, 16, (3, 3), 1, 1, 1, add=-2.1415)
        )
        self.conv_con2_phase = nn.Sequential(
            LocallyConnected2d(16, 1, 63, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            GeneralELU(-2.1415),
        )

        self.conv8_phase = nn.Sequential(
             *conv_phase(1, 4, (3, 3), 1, 1, 1, add=-2.1415)
        )
        self.conv9_phase = nn.Sequential(
             *conv_phase(4, 8, (3, 3), 1, 1, 1, add=-2.1415)
        )
        self.conv10_phase = nn.Sequential(
             *conv_phase(8, 12, (3, 3), 1, 2, 2, add=-2.1415)
        )
        self.conv_con3_phase = nn.Sequential(
            LocallyConnected2d(12, 1, 63, 1, stride=1, bias=False),
            nn.BatchNorm2d(1),
            GeneralELU(-2.1415),
        )
        self.symmetry_imag = Lambda(partial(symmetry, mode='imag'))

    def forward(self, x):
        inp = x.clone()
        phase = x[:, 1, :].unsqueeze(1)

        # First block
        phase = self.conv1_phase(phase)

        phase = self.conv2_phase(phase)

        phase = self.conv3_phase(phase)

        phase = self.conv_con1_phase(phase)

        # Second block
        phase = self.conv4_phase(phase)

        phase = self.conv5_phase(phase)

        phase = self.conv6_phase(phase)

        phase = self.conv7_phase(phase)

        phase = self.conv_con2_phase(phase)

        # Third block
        phase = self.conv8_phase(phase)

        phase = self.conv9_phase(phase)

        phase = self.conv10_phase(phase)

        phase = self.conv_con3_phase(phase)

        phase = phase + inp[:, 1].unsqueeze(1)
        x1 = self.symmetry_imag(phase).reshape(-1, 1, 63, 63)
        return x1


from dl_framework.uncertainty_arch import (
    block_1_a,
    block_2_a,
    block_3_a,
    block_1_a_unc,
    block_2_a_unc,
    block_3_a_unc,
)


class filter_deep_amp_unc(nn.Module):
    def __init__(self):
        super().__init__()
        self.block1 = block_1_a()
        self.block2 = block_2_a()
        self.block3 = block_3_a()
        self.block1_unc = block_1_a_unc()
        self.block2_unc = block_2_a_unc()
        self.block3_unc = block_3_a_unc()
        self.symmetry = Lambda(symmetry)
        self.elu = GeneralELU(add=+1)
        self.elu_unc = GeneralELU(add=+1+1e-5)

    def forward(self, x):
        x = x[:, 0].unsqueeze(1)
        inp = x.clone()

        # Blocks to predict amp
        x0 = self.block1(x)
        x0 = self.block2(x0)
        x0 = self.block3(x0)

        # x0 = x0.clone()
        # x0 = x0 + inp
        x0 = self.symmetry(x0[:, 0]).reshape(-1, 1, 63, 63)
        # x0 = self.elu(x0)
        x0[inp != 0] = inp[inp != 0]

        # Blocks to predict uncertainty
        x1 = self.block1_unc(x)
        x1 = self.block2_unc(x1)
        x1 = self.block3_unc(x1)

        # x1 = x1.clone()
        x1 = self.symmetry(x1[:, 0]).reshape(-1, 1, 63, 63)
        # x1 = self.elu_unc(x1)
        x1[inp != 0] = 1e-8

        out = torch.cat([x0, x1, inp], dim=1)
        return out


from dl_framework.uncertainty_arch import (
    block_1_p,
    block_2_p,
    block_3_p,
    block_4_p,
    bridge,
    block_1_p_unc,
    block_2_p_unc,
    block_3_p_unc,
)


class filter_deep_phase_unc(nn.Module):
    def __init__(self):
        super().__init__()
        self.block1 = block_1_p()
        self.block2 = block_2_p()
        self.block3 = block_3_p()
        self.block4 = block_4_p()
        self.bridge = bridge()
        self.block1_unc = block_1_p_unc()
        self.block2_unc = block_2_p_unc()
        self.block3_unc = block_3_p_unc()
        self.symmetry = Lambda(partial(symmetry, mode="imag"))
        self.symmetry_unc = Lambda(symmetry)
        self.elu_phase = GeneralELU(add=-(pi - 1), maxv=pi)
        self.elu = GeneralELU(add=+(1e-5))
        self.phase_range = Lambda(phase_range)

    def forward(self, x):
        x = x[:, 1].unsqueeze(1)
        inp = x.clone()

        # Blocks to predict phase
        x0 = self.block1(x)
        b2 = self.block2(x0)
        b3 = self.block3(x0)
        x0 = self.bridge(torch.cat([inp, b2, b3], dim=1))
        x0 = self.block4(x0)

        x0 = x0.clone()
        x0 = x0 + inp
        # x0 = self.phase_range(x0)
        x0[inp != 0] = inp[inp != 0]
        x0 = self.symmetry(x0[:, 0]).reshape(-1, 1, 63, 63)
        # x0 = self.elu_phase(x0)

        # Blocks to predict uncertainty
        x1 = self.block1_unc(x)
        x1 = self.block2_unc(x1)
        x1 = self.block3_unc(x1)

        x1 = self.symmetry_unc(x1[:, 0]).reshape(-1, 1, 63, 63)
        x1[inp != 0] = 1e-8

        out = torch.cat([x0, x1, inp], dim=1)
        return out


from dl_framework.model import split_parts, combine_parts
from dl_framework.uncertainty_arch import block_1_p_32, block_2_p_32, block_1_p_31, block_2_p_31


class phase_parts(nn.Module):
    def __init__(self):
        super().__init__()
        self.part1_block1 = block_1_p_32()
        self.part1_block2 = block_2_p_32()
        self.part2_block1 = block_1_p_31()
        self.part2_block2 = block_2_p_31()
        self.part3_block1 = block_1_p_32()
        self.part3_block2 = block_2_p_32()
        self.part4_block1 = block_1_p_32()
        self.part4_block2 = block_2_p_32()
        self.split_parts = Lambda(split_parts)
        self.combine_parts = Lambda(combine_parts)
        self.symmetry = Lambda(partial(symmetry, mode="imag"))

    def forward(self, x):
        x = x[:, 1].unsqueeze(1)
        inp = x.clone()
        bs = x.shape[0]

        part1, part2, part3, part4 = self.split_parts(x)

        # part1
        part1 = self.part1_block1(part1)
        part1 = self.part1_block2(part1)

        # part2
        part2 = self.part2_block1(part2)
        part2 = self.part2_block2(part2)

        # part3
        part3 = self.part3_block1(part3)
        part3 = self.part3_block2(part3)

        # part4
        part4 = self.part4_block1(part4)
        part4 = self.part4_block2(part4)

        # combine
        phase = self.combine_parts([part1, part2, part3, part4, (bs, 1, 63, 63)])
        phase = phase + inp
        phase = self.symmetry(phase[:, 0]).reshape(-1, 1, 63, 63)
        return phase


class phase_parts_3d(nn.Module):
    def init(self):
        super().init()
        self.part1_block1 = block_1_p_32()
        self.part1_block2 = block_2_p_32()
        self.part1_1 = local_block()
        self.part1_local = local_p_32()
        self.part2_block1 = block_1_p_32()
        self.part2_block2 = block_2_p_32()
        self.part2_1 = local_block()
        self.part2_local = local_p_32()
        self.part3_block1 = block_1_p_32()
        self.part3_block2 = block_2_p_32()
        self.part3_1 = local_block()
        self.part3_local = local_p_32()
        self.part4_block1 = block_1_p_32()
        self.part4_block2 = block_2_p_32()
        self.part4_1 = local_block()
        self.part4_local = local_p_32()
        self.conv_3d_12 = nn.Conv3d(1, 12, 3, 1, 1, 1)
        self.conv_3d_34 = nn.Conv3d(1, 12, 3, 1, 1, 1)
        self.split_parts = Lambda(split_parts)
        self.combine_parts = Lambda(combine_parts)
        self.symmetry = Lambda(partial(symmetry, mode="imag"))

    def forward(self, x):
        x = x[:, 1].unsqueeze(1)
        inp = x.clone()
        bs = x.shape[0]

        part1, part2, part3, part4 = self.split_parts(x)

        # part1
        part1 = self.part1_block1(part1)
        part1 = self.part1_block2(part1)
        p1 = self.part1_1(part1)

        # part2
        part2 = self.part2_block1(part2)
        part2 = self.part2_block2(part2)
        p2 = self.part2_1(part2)

        p1 = p1.unsqueeze(2)
        p2 = p2.unsqueeze(2)
        part12 = torch.cat([p1, p2], dim=2)
        part12 = self.conv_3d_12(part12)
        part12 = part12.reshape(bs, 24, 32, 32)

        part1 = torch.cat([part1, part12], dim=1)
        part1 = self.part1_local(part1)
        part2 = torch.cat([part2, part12], dim=1)
        part2 = self.part2_local(part2)

        # part3
        part3 = self.part3_block1(part3)
        part3 = self.part3_block2(part3)
        p3 = self.part3_1(part3)

        # part4
        part4 = self.part4_block1(part4)
        part4 = self.part4_block2(part4)
        p4 = self.part4_1(part4)

        p3 = p3.unsqueeze(2)
        p4 = p4.unsqueeze(2)
        part34 = torch.cat([p3, p4], dim=2)
        part34 = self.conv_3d_34(part34)
        part34 = part34.reshape(bs, 24, 32, 32)

        part3 = torch.cat([part3, part34], dim=1)
        part3 = self.part3_local(part1)
        part4 = torch.cat([part4, part34], dim=1)
        part4 = self.part4_local(part4)

        # combine
        phase = self.combine_parts([part1, part2, part3, part4, (bs, 1, 63, 63)])
        phase = phase + inp
        phase = self.symmetry(phase[:, 0]).reshape(-1, 1, 63, 63)
        return phase
