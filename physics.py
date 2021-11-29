import torch
import numpy as np
import torch.nn.functional as F
from torch.nn.modules.utils import _quadruple


class SobelFilter(object):
    def __init__(self, imsize, correct=True, device="cpu"):
        # conv2d is cross-correlation, need to transpose the kernel here
        self.HSOBEL_WEIGHTS_3x3 = (
            torch.FloatTensor(np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]) / 8.0)
            .unsqueeze(0)
            .unsqueeze(0)
            .to(device)
        )

        self.VSOBEL_WEIGHTS_3x3 = self.HSOBEL_WEIGHTS_3x3.transpose(-1, -2)

        self.SOBEL_WEIGHTS_TEMP = (
            torch.FloatTensor(np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]]) / 1.0)
            .unsqueeze(0)
            .unsqueeze(0)
            .to(device)
        )

        self.SOBEL_WEIGHTS_TEMP_H_UP = (
            torch.FloatTensor(np.array([[0, 0, 0], [1, 1, 0], [0, 0, 0]]) / 2.0)
            .unsqueeze(0)
            .unsqueeze(0)
            .to(device)
        )

        self.SOBEL_WEIGHTS_TEMP_H_DOWN = (
            torch.FloatTensor(np.array([[0, 0, 0], [0, 1, 1], [0, 0, 0]]) / 2.0)
            .unsqueeze(0)
            .unsqueeze(0)
            .to(device)
        )

        self.SOBEL_WEIGHTS_TEMP_V_UP = self.SOBEL_WEIGHTS_TEMP_H_UP.transpose(-1, -2)

        self.SOBEL_WEIGHTS_TEMP_V_DOWN = self.SOBEL_WEIGHTS_TEMP_H_DOWN.transpose(
            -1, -2
        )

        self.VSOBEL_WEIGHTS_5x5 = (
            torch.FloatTensor(
                np.array(
                    [
                        [-5, -4, 0, 4, 5],
                        [-8, -10, 0, 10, 8],
                        [-10, -20, 0, 20, 10],
                        [-8, -10, 0, 10, 8],
                        [-5, -4, 0, 4, 5],
                    ]
                )
                / 240.0
            )
            .unsqueeze(0)
            .unsqueeze(0)
            .to(device)
        )
        self.HSOBEL_WEIGHTS_5x5 = self.VSOBEL_WEIGHTS_5x5.transpose(-1, -2)

        modifier = np.eye(imsize)
        modifier[0:2, 0] = np.array([4, -1])
        modifier[-2:, -1] = np.array([-1, 4])
        self.modifier = torch.FloatTensor(modifier).to(device)
        self.correct = correct

    def grad_h(self, image, filter_size=3):
        """Get image gradient along horizontal direction, or x axis.
        Option to do replicate padding for image before convolution. This is mainly
        for estimate the du/dy, enforcing Neumann boundary condition.

        Args:
            image (Tensor): (1, 1, H, W)
            replicate_pad (None, int, 4-tuple): if 4-tuple, (padLeft, padRight, padTop,
                padBottom)
        """
        image_width = image.shape[-1]

        if filter_size == 3:
            replicate_pad = 1
            kernel = self.VSOBEL_WEIGHTS_3x3
        elif filter_size == 5:
            replicate_pad = 2
            kernel = self.VSOBEL_WEIGHTS_5x5
        else:
            raise NotImplementedError("unssported filter size")

        image = F.pad(image, _quadruple(replicate_pad), mode="replicate")
        grad = F.conv2d(image, kernel, stride=1, padding=0, bias=None) * image_width
        # modify the boundary based on forward & backward finite difference (three points)
        # forward [-3, 4, -1], backward [3, -4, 1]
        if self.correct:
            return torch.matmul(grad, self.modifier)
        else:
            return grad

    def grad_h_temp_up(self, image, filter_size=3):
        """Get image gradient along horizontal direction, or x axis.
        Option to do replicate padding for image before convolution. This is mainly
        for estimate the du/dy, enforcing Neumann boundary condition.

        Args:
            image (Tensor): (1, 1, H, W)
            replicate_pad (None, int, 4-tuple): if 4-tuple, (padLeft, padRight, padTop,
                padBottom)
        """
        image_width = image.shape[-1]

        if filter_size == 3:
            replicate_pad = 1
            kernel = self.SOBEL_WEIGHTS_TEMP_H_UP
            # kernel = self.HSOBEL_WEIGHTS_3x3
        elif filter_size == 5:
            replicate_pad = 2
            kernel = self.VSOBEL_WEIGHTS_5x5
        else:
            raise NotImplementedError("unssported filter size")

        image = F.pad(image, _quadruple(replicate_pad), mode="replicate")
        grad = F.conv2d(image, kernel, stride=1, padding=0, bias=None) * image_width
        # modify the boundary based on forward & backward finite difference (three points)
        # forward [-3, 4, -1], backward [3, -4, 1]
        if self.correct:
            return torch.matmul(grad, self.modifier)
        else:
            return grad

    def grad_h_temp_down(self, image, filter_size=3):
        """Get image gradient along horizontal direction, or x axis.
        Option to do replicate padding for image before convolution. This is mainly
        for estimate the du/dy, enforcing Neumann boundary condition.

        Args:
            image (Tensor): (1, 1, H, W)
            replicate_pad (None, int, 4-tuple): if 4-tuple, (padLeft, padRight, padTop,
                padBottom)
        """
        image_width = image.shape[-1]

        if filter_size == 3:
            replicate_pad = 1
            kernel = self.SOBEL_WEIGHTS_TEMP_H_DOWN
            # kernel = self.HSOBEL_WEIGHTS_3x3
        elif filter_size == 5:
            replicate_pad = 2
            kernel = self.VSOBEL_WEIGHTS_5x5
        else:
            raise NotImplementedError("unssported filter size")

        image = F.pad(image, _quadruple(replicate_pad), mode="replicate")
        grad = F.conv2d(image, kernel, stride=1, padding=0, bias=None) * image_width
        # modify the boundary based on forward & backward finite difference (three points)
        # forward [-3, 4, -1], backward [3, -4, 1]
        if self.correct:
            return torch.matmul(grad, self.modifier)
        else:
            return grad

    def grad_v_temp_up(self, image, filter_size=3):
        """Get image gradient along horizontal direction, or x axis.
        Option to do replicate padding for image before convolution. This is mainly
        for estimate the du/dy, enforcing Neumann boundary condition.

        Args:
            image (Tensor): (1, 1, H, W)
            replicate_pad (None, int, 4-tuple): if 4-tuple, (padLeft, padRight, padTop,
                padBottom)
        """
        image_width = image.shape[-1]

        if filter_size == 3:
            replicate_pad = 1
            kernel = self.SOBEL_WEIGHTS_TEMP_V_UP
            # kernel = self.VSOBEL_WEIGHTS_3x3
        elif filter_size == 5:
            replicate_pad = 2
            kernel = self.VSOBEL_WEIGHTS_5x5
        else:
            raise NotImplementedError("unssported filter size")

        image = F.pad(image, _quadruple(replicate_pad), mode="replicate")
        grad = F.conv2d(image, kernel, stride=1, padding=0, bias=None) * image_width
        # modify the boundary based on forward & backward finite difference (three points)
        # forward [-3, 4, -1], backward [3, -4, 1]
        if self.correct:
            return torch.matmul(grad, self.modifier)
        else:
            return grad

    def grad_v_temp_down(self, image, filter_size=3):
        """Get image gradient along horizontal direction, or x axis.
        Option to do replicate padding for image before convolution. This is mainly
        for estimate the du/dy, enforcing Neumann boundary condition.

        Args:
            image (Tensor): (1, 1, H, W)
            replicate_pad (None, int, 4-tuple): if 4-tuple, (padLeft, padRight, padTop,
                padBottom)
        """
        image_width = image.shape[-1]

        if filter_size == 3:
            replicate_pad = 1
            kernel = self.SOBEL_WEIGHTS_TEMP_V_DOWN
            # kernel = self.VSOBEL_WEIGHTS_3x3
        elif filter_size == 5:
            replicate_pad = 2
            kernel = self.VSOBEL_WEIGHTS_5x5
        else:
            raise NotImplementedError("unssported filter size")

        image = F.pad(image, _quadruple(replicate_pad), mode="replicate")
        grad = F.conv2d(image, kernel, stride=1, padding=0, bias=None) * image_width
        # modify the boundary based on forward & backward finite difference (three points)
        # forward [-3, 4, -1], backward [3, -4, 1]
        if self.correct:
            return torch.matmul(grad, self.modifier)
        else:
            return grad

    def grad_temp(self, image, filter_size=3):
        """Get image gradient along horizontal direction, or x axis.
        Option to do replicate padding for image before convolution. This is mainly
        for estimate the du/dy, enforcing Neumann boundary condition.

        Args:
            image (Tensor): (1, 1, H, W)
            replicate_pad (None, int, 4-tuple): if 4-tuple, (padLeft, padRight, padTop,
                padBottom)
        """
        image_width = image.shape[-1]

        if filter_size == 3:
            replicate_pad = 1
            kernel = self.SOBEL_WEIGHTS_TEMP
        elif filter_size == 5:
            replicate_pad = 2
            kernel = self.VSOBEL_WEIGHTS_5x5
        else:
            raise NotImplementedError("unssported filter size")

        image = F.pad(image, _quadruple(replicate_pad), mode="replicate")
        grad = F.conv2d(image, kernel, stride=1, padding=0, bias=None) * image_width
        # modify the boundary based on forward & backward finite difference (three points)
        # forward [-3, 4, -1], backward [3, -4, 1]
        if self.correct:
            return torch.matmul(grad, self.modifier)
        else:
            return grad

    def grad_v(self, image, filter_size=3):
        image_height = image.shape[-2]
        if filter_size == 3:
            replicate_pad = 1
            kernel = self.HSOBEL_WEIGHTS_3x3
        elif filter_size == 5:
            replicate_pad = 2
            kernel = self.HSOBEL_WEIGHTS_5x5
        else:
            raise NotImplementedError("unssported filter size")

        image = F.pad(image, _quadruple(replicate_pad), mode="replicate")
        grad = F.conv2d(image, kernel, stride=1, padding=0, bias=None) * image_height
        # modify the boundary based on forward & backward finite difference
        if self.correct:
            return torch.matmul(self.modifier.t(), grad)
        else:
            return grad


def constitutive_constraint(input, output, sobel_filter):
    """sigma = - K * grad(u)

    Args:
        input (Tensor): (1, 3, 65, 65)
        output (Tensor): (1, 1, 65, 65),
            three channels from 0-2: u, sigma_1, sigma_2
    """
    thermal_conductivity = 0.01

    totalEnergy = thermal_conductivity * sobel_filter.grad_temp(
        output
    )  # Delta T in x direction

    return (totalEnergy ** 2).mean()