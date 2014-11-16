//
//  SignInController.m
//  hooCal
//
//  Created by zhongtoby on 14/11/15.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import "SignInController.h"
#import "SignInViewModel.h"
#import <SVProgressHUD.h>
#import "EventListController.h"

@interface SignInController () <UITextFieldDelegate>
@property (strong, nonatomic) IBOutlet UITextField *emailField;
@property (strong, nonatomic) IBOutlet UITextField *pswField;
@end

@implementation SignInController
#pragma mark - action
- (IBAction)cancel:(id)sender {
    [self resignKeyboard];
    [self.navigationController dismissViewControllerAnimated:YES completion:nil];
}
- (IBAction)signIn:(id)sender {
    [self resignKeyboard];
    [SVProgressHUD showWithStatus:@"正在登录"];
//    __weak UIViewController *weakSelf = self;
    [SignInViewModel signWithEmail:_emailField.text Psw:_pswField.text Block:^(NSInteger state, NSDictionary *dict) {
        if (state == successful) {
            [SVProgressHUD dismiss];
//            __weak UINavigationController *weakSelf = (UINavigationController *)self.parentViewController;
//            [self.navigationController dismissViewControllerAnimated:YES completion:^{
//                EventListController *eventListController = [[EventListController alloc] init];
                [self performSegueWithIdentifier:@"segueAfterSignIn" sender:nil];
//            }];
        } else {
            [SVProgressHUD showErrorWithStatus:@"登录失败"];
        }
    }];
}

- (void)touchesBegan:(NSSet *)touches withEvent:(UIEvent *)event {
    [self resignKeyboard];
}

#pragma mark - tools
- (void)resignKeyboard {
    [_emailField resignFirstResponder];
    [_pswField resignFirstResponder];
}

#pragma mark - UITextFieldDelegate
- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    if (textField.tag == 1) {
        [_pswField becomeFirstResponder];
    } else {
        [textField resignFirstResponder];
        [self signIn:nil];
    }
    return YES;
}

@end
